#!/usr/bin/env python
# -*- coding: utf-8 -*

import dpdata
import numpy as np
from deepmd.infer import DeepPot

from sclmd.tools import get_atommass


class deepmddriver():
    def __init__(self, strinfile, fmt, pbinfile, md2ang=0.06466):
        self.deepmdstr(strinfile, fmt, md2ang)
        self.dpstart(pbinfile)

    def deepmdstr(self, strinfile, fmt, md2ang):
        str = dpdata.LabeledSystem(strinfile, fmt)
        #str.to('lammps/lmp', 'data.lmp', frame_idx=0)
        #str.to('vasp/poscar', 'POSCAR.vasp', frame_idx=0)
        self.number = sum(str['atom_types'])
        self.type = str['atom_types']
        atomname = str['atom_names']
        mass = [get_atommass(el) for el in atomname]
        self.els = []
        atomnamelist = []
        for type in self.type:
            self.els.append(mass[type])
            atomnamelist.append(atomname[type])
        self.xyz = str['coords'].flatten()
        self.conv = md2ang*np.array([3*[1.0/np.sqrt(mass)]
                                     for mass in self.els]).flatten()
        self.axyz = []
        for i, a in enumerate(self.els):
            self.axyz.append([atomnamelist[i], self.xyz[i*3],
                              self.xyz[i*3+1], self.xyz[i*3+2]])
        self.cell = str['cells']
        print("structure imported")

    def dpstart(self, pbinfile):
        self.dp = DeepPot(pbinfile)
        print("deepmdkit launched")
        # print(self.conv.shape)
        self.initforce()

    def newx(self, q):
        return self.xyz + self.conv*q

    def absforce(self, q):
        self.e, self.f, self.v = self.dp.eval(
            self.newx(q), self.cell, self.type)
        return self.conv*np.array(self.f)

    def initforce(self):
        print("Calculate zero displacement force")
        self.f0 = self.absforce(np.zeros(3*self.number))

    def force(self, q):
        return self.absforce(q) - self.f0

    def energy(self):
        return self.e