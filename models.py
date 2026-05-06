import numpy as np

class Room:
    def __init__(self, m, n, windows, doors, tops, heater1, heater2, times_len, start_temp=18+273.15):
        self.M = m
        self.N = n
        self.windows = windows
        self.doors = doors
        self.tops = tops
        self.h1 = heater1
        self.h2 = heater2

        ib1 = [i for i in range(m*n) if i % m == 0]
        ib2 = [i for i in range(m*n) if (i+1) % m == 0]
        ib3 = [i for i in range(m*n) if i < m]
        ib4 = [i for i in range(m*n) if i > m*(n-1)]

        ib1prim = [i for i in range(m*n) if i % m == 1]
        ib2prim = [i for i in range(m*n) if (i+2) % m == 0]
        ib3prim = [i+m for i in range(m*n) if i < m]
        ib4prim = [i-m for i in range(m*n) if i > m*(n-1)]

        self.walls = ib1 + ib2 + ib3 + ib4
        self.wallsprim = ib1prim + ib2prim + ib3prim + ib4prim

        self.laplasjan()
        self.u = np.zeros((times_len, self.M * self.N))
        self.u[0, :] = [start_temp] * (self.N * self.M)
        
        self.epsilon = 800 / (1.2 * 1 * 0.05 * 1005)
        self.power = 0

    def set_initial_windows(self, window_temp):
        """Sets the initial temperature in the windows for t=0"""
        self.u[0, self.windows] = [window_temp] * len(self.windows)

    def laplasjan(self):
        D2x = np.diag(-2 * np.ones(self.M)) + np.diag(np.ones(self.M - 1), 1) + np.diag(np.ones(self.M - 1), -1)
        D2y = np.diag(-2 * np.ones(self.N)) + np.diag(np.ones(self.N - 1), 1) + np.diag(np.ones(self.N - 1), -1)
        self.L = np.kron(np.eye(self.N), D2x) + np.kron(D2y, np.eye(self.M))

    def update(self, t, window_temp, hx, ht, typ=1, turn_off_range=None):
        self.u[t, :] = self.u[t-1, :] + (ht / hx**2) * np.matmul(self.L, self.u[t-1, :])
        
        # Check if we are in the scheduled off period
        is_off_schedule = turn_off_range is not None and t in turn_off_range
        
        if self.u[t, int(self.M * self.N / 2 + self.M / 2)] > 21 + 273.15 or is_off_schedule:
            heater_on = 0
        else:
            heater_on = 1
            
        if typ == 1:
            self.u[t, self.h1] += self.epsilon * heater_on
            self.power += self.epsilon * heater_on
        elif typ == 2:
            self.u[t, self.h2] += self.epsilon * heater_on
            self.power += self.epsilon * heater_on

        self.u[t, self.walls] = self.u[t, self.wallsprim]
        self.u[t, self.windows] = [window_temp] * len(self.windows)

class Apartment:
    def __init__(self, rooms, K, times_len):
        self.rooms = rooms
        self.K = K

        ib1 = [i for i in range(K*K) if i % K == 0]
        ib2 = [i for i in range(K*K) if (i+1) % K == 0]
        ib3 = [i for i in range(K*K) if i < K]
        ib4 = [i for i in range(K*K) if i >= K*(K-1)]
        ib5 = [i for i in range(int(2/5*K*K), int(2/5*K*K+K))]
        ib6 = [i for i in range(0, int(2/5*K*K)) if i % K == int(3/5*K)]
        ib7 = [i for i in range(int(2/5*K*K-K), int(2/5*K*K))]
        ib8 = [i for i in range(0, int(2/5*K*K)) if (i+1) % K == int(3/5*K)]

        i_len = len(ib8)
        del ib8[int(i_len*1/4): int(i_len*3/4)]
        del ib6[int(i_len*1/4): int(i_len*3/4)]
        del ib5[20:40]
        del ib7[20:40]

        del ib3[20:39]
        del ib3[51:69]
        del ib4[19:39]
        del ib4[49:69]

        self.walls = ib1 + ib2 + ib3 + ib4 + ib5 + ib6 + ib7 + ib8
        self.u = np.zeros((times_len, K*K))
        self.merge(0)

    def update(self, t, window_temp, hx, ht, typ=1, turn_off_range=None):
        for room in self.rooms:
            room.update(t, window_temp, hx, ht, typ, turn_off_range)

    def merge(self, t):
        pok1, pok2, pok3 = self.rooms[0], self.rooms[1], self.rooms[2]

        pok1.u[t, pok1.doors], pok2.u[t, pok2.doors[0]] = (pok1.u[t, pok1.doors] + pok2.u[t, pok2.doors[0]]) / 2, (pok1.u[t, pok1.doors] + pok2.u[t, pok2.doors[0]]) / 2
        pok2.u[t, pok2.doors[1]], pok3.u[t, pok3.doors] = (pok2.u[t, pok2.doors[1]] + pok3.u[t, pok3.doors]) / 2, (pok2.u[t, pok2.doors[1]] + pok3.u[t, pok3.doors]) / 2

        self.u[t, range(pok1.tops[0], pok1.tops[3]+1)] = pok1.u[t, :] - [273.15] * (pok1.M * pok1.N)
        
        p2 = [i for i in range(pok2.tops[0], pok2.tops[3]+1) if i % self.K <= pok2.tops[2]]
        p3 = [i for i in range(pok3.tops[0], pok3.tops[3]+1) if i % self.K >= pok3.tops[0]]
        
        self.u[t, p2] = pok2.u[t, :] - [273.15] * (pok2.M * pok2.N)
        self.u[t, p3] = pok3.u[t, :] - [273.15] * (pok3.M * pok3.N)
        self.u[t, self.walls] = [np.nan] * len(self.walls)