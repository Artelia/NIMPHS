# -*- coding: utf8 -*-
# <pep8 compliant>


import os
import sys
from builtins import bytes
from struct import unpack, pack
import numpy as np
import copy
import mmap
import matplotlib.tri as tri
import datetime
import gc


class Serafin:
    # Français
    # French
    nomvar2d = ['VITESSE U       M/S             ',
                'VITESSE V       M/S             ',
                'CELERITE        M/S             ',
                "HAUTEUR D'EAU   M               ",
                'SURFACE LIBRE   M               ',
                'FOND            M               ',
                'FROUDE                          ',
                'DEBIT SCALAIRE  M2/S            ',
                'TRACEUR                         ',
                'ENERGIE TURBUL. JOULE/KG        ',
                'DISSIPATION     WATT/KG         ',
                'VISCOSITE TURB. M2/S            ',
                'DEBIT SUIVANT X M2/S            ',
                'DEBIT SUIVANT Y M2/S            ',
                'VITESSE SCALAIREM/S             ',
                'VENT X          M/S             ',
                'VENT Y          M/S             ',
                'PRESSION ATMOS. PASCAL          ',
                'FROTTEMENT                      ',
                'DERIVE EN X     M               ',
                'DERIVE EN Y     M               ',
                'NBRE DE COURANT                 ',
                'COTE MAXIMUM    M               ',
                'TEMPS COTE MAXI S               ',
                'VITESSE MAXIMUM M/S             ',
                'T VITESSE MAXI  S               ']
    nomvar3d = ['COTE Z          M               ',
                'VITESSE U       M/S             ',
                'VITESSE V       M/S             ',
                'VITESSE W       M/S             ',
                'NUX POUR VITESSEM2/S            ',
                'NUY POUR VITESSEM2/S            ',
                'NUZ POUR VITESSEM2/S            ',
                'ENERGIE TURBULENJOULE/KG        ',
                'DISSIPATION     WATT/KG         ',
                'NB DE RICHARDSON                ',
                'DENSITE RELATIVE                ',
                'PRESSION DYNAMIQPA              ',
                'PRESSION HYDROSTPA              ',
                'U CONVECTION    M/S             ',
                'V CONVECTION    M/S             ',
                'W CONVECTION    M/S             ',
                'VOLUMES TEMPS N M3              ',
                'DM1                             ',
                'DHHN            M               ',
                'UCONVC          M/S             ',
                'VCONVC          M/S             ',
                'UD              M/S             ',
                'VD              M/S             ',
                'WD              M/S             ',
                'PRIVE 1         ?               ',
                'PRIVE 2         ?               ',
                'PRIVE 3         ?               ',
                'PRIVE 4         ?               ']
    # Anglais
    nomvar2d_ENG = ['VELOCITY U      M/S             ',
                    'VELOCITY V      M/S             ',
                    'CELERITY        M/S             ',
                    'WATER DEPTH     M               ',
                    'FREE SURFACE    M               ',
                    'BOTTOM          M               ',
                    'FROUDE NUMBER                   ',
                    'SCALAR FLOWRATE M2/S            ',
                    'EX TRACER                       ',
                    'TURBULENT ENERG.JOULE/KG        ',
                    'DISSIPATION     WATT/KG         ',
                    'VISCOSITY       M2/S            ',
                    'FLOWRATE ALONG XM2/S            ',
                    'FLOWRATE ALONG YM2/S            ',
                    'SCALAR VELOCITY M/S             ',
                    'WIND ALONG X    M/S             ',
                    'WIND ALONG Y    M/S             ',
                    'AIR PRESSURE    PASCAL          ',
                    'BOTTOM FRICTION                 ',
                    'DRIFT ALONG X   M               ',
                    'DRIFT ALONG Y   M               ',
                    'COURANT NUMBER                  ',
                    'VARIABLE 23     UNIT   ??       ',
                    'VARIABLE 24     UNIT   ??       ',
                    'VARIABLE 25     UNIT   ??       ',
                    'VARIABLE 26     UNIT   ??       ',
                    'HIGH WATER MARK M               ',
                    'HIGH WATER TIME S               ',
                    'HIGHEST VELOCITYM/S             ',
                    'TIME OF HIGH VELS               ',
                    'FRICTION VEL.   M/S             ']
    nomvar3d_ENG = ['ELEVATION Z     M               ',
                    'VELOCITY U      M/S             ',
                    'VELOCITY V      M/S             ',
                    'VELOCITY W      M/S             ',
                    'NUX FOR VELOCITYM2/S            ',
                    'NUY FOR VELOCITYM2/S            ',
                    'NUZ FOR VELOCITYM2/S            ',
                    'TURBULENT ENERGYJOULE/KG        ',
                    'DISSIPATION     WATT/KG         ',
                    'RICHARDSON NUMB                 ',
                    'RELATIVE DENSITY                ',
                    'DYNAMIC PRESSUREPA              ',
                    'HYDROSTATIC PRESPA              ',
                    'U ADVECTION     M/S             ',
                    'V ADVECTION     M/S             ',
                    'W ADVECTION     M/S             ',
                    'DM1                             ',
                    'DHHN            M               ',
                    'UCONVC          M/S             ',
                    'VCONVC          M/S             ',
                    'UD              M/S             ',
                    'VD              M/S             ',
                    'WD              M/S             ',
                    'PRIVE 1         ?               ',
                    'PRIVE 2         ?               ',
                    'PRIVE 3         ?               ',
                    'PRIVE 4         ?               ']
    # English
    nomvar2d_ENG = ['VELOCITY U      M/S             ',
                    'VELOCITY V      M/S             ',
                    'CELERITY        M/S             ',
                    'WATER DEPTH     M               ',
                    'FREE SURFACE    M               ',
                    'BOTTOM          M               ',
                    'FROUDE NUMBER                   ',
                    'SCALAR FLOWRATE M2/S            ',
                    'EX TRACER                       ',
                    'TURBULENT ENERG.JOULE/KG        ',
                    'DISSIPATION     WATT/KG         ',
                    'VISCOSITY       M2/S            ',
                    'FLOWRATE ALONG XM2/S            ',
                    'FLOWRATE ALONG YM2/S            ',
                    'SCALAR VELOCITY M/S             ',
                    'WIND ALONG X    M/S             ',
                    'WIND ALONG Y    M/S             ',
                    'AIR PRESSURE    PASCAL          ',
                    'BOTTOM FRICTION                 ',
                    'DRIFT ALONG X   M               ',
                    'DRIFT ALONG Y   M               ',
                    'COURANT NUMBER                  ',
                    'VARIABLE 23     UNIT   ??       ',
                    'VARIABLE 24     UNIT   ??       ',
                    'VARIABLE 25     UNIT   ??       ',
                    'VARIABLE 26     UNIT   ??       ',
                    'HIGH WATER MARK M               ',
                    'HIGH WATER TIME S               ',
                    'HIGHEST VELOCITYM/S             ',
                    'TIME OF HIGH VELS               ',
                    'FRICTION VEL.   M/S             ']
    nomvar3d_ENG = ['ELEVATION Z     M               ',
                    'VELOCITY U      M/S             ',
                    'VELOCITY V      M/S             ',
                    'VELOCITY W      M/S             ',
                    'NUX FOR VELOCITYM2/S            ',
                    'NUY FOR VELOCITYM2/S            ',
                    'NUZ FOR VELOCITYM2/S            ',
                    'TURBULENT ENERGYJOULE/KG        ',
                    'DISSIPATION     WATT/KG         ',
                    'RICHARDSON NUMB                 ',
                    'RELATIVE DENSITY                ',
                    'DYNAMIC PRESSUREPA              ',
                    'HYDROSTATIC PRESPA              ',
                    'U ADVECTION     M/S             ',
                    'V ADVECTION     M/S             ',
                    'W ADVECTION     M/S             ',
                    'DM1                             ',
                    'DHHN            M               ',
                    'UCONVC          M/S             ',
                    'VCONVC          M/S             ',
                    'UD              M/S             ',
                    'VD              M/S             ',
                    'WD              M/S             ',
                    'PRIVE 1         ?               ',
                    'PRIVE 2         ?               ',
                    'PRIVE 3         ?               ',
                    'PRIVE 4         ?               ']

    def __init__(self, name='', mode='rb',
                 read_time=False,
                 pdt_variable=False,
                 paral=False):

        self.name = [name]
        self.mode = mode
        self.paral = paral
        self.ncsize = 1
        self.size_num_paral = 5  # Size of the number in the name of the file partitionned
        self.nplan = 1
        self.FILE = []
        # Open the file
        self.open()
        self.endian = '>'
        self.precision = ['f', 4]
        self.format = 'telemac'
        self.title = ''
        self.nbvar = 0
        self.nbvar2 = 0
        self.nomvar = []
        self.date = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.date_supp = []
        self.date_ref = None
        # self.nelem = 0
        # self.npoin = 0
        self.ndp = 0  # Nombre de points
        self.var_i = 1
        # self.ikle = np.array([], dtype='int32')
        # self.IPOBO = np.array([], dtype='int32')
        # self.x = np.array([])
        # self.y = np.array([])
        # self.entete = 0
        # self.taille_pdt = 0
        self.nb_pdt = 0  # Nombre de pas de temps
        self.taille_fichier = 0
        self.pos_fic = 0
        self.pos_pdt = 0
        self.first_error = True
        self.first_continuous = True

        self.temps = []
        self.min_elem = 99999999.
        self.max_elem = 0.
        self.min_surface = 99999999.
        self.max_surface = 0.
        self.surface = 0.

        self.FindH = False
        self.PosH = -1
        self.PosSL = -1
        self.PosZ = -1
        self.PosU = -1
        self.PosV = -1
        self.PosW = -1

        # 2D variables
        # self.is_get_2d = False
        # self.npoin2d = 0
        # self.ikle2d = None
        # self.nelem2d = None
        # self.x2d = None
        # self.y2d = None
        # self.neighbors = None
        self.neighbors_tri = None  # Voisins (tri = triangle)
        self.edges_corresp = None
        self.dico_edges = {}
        self.boundaries_node = None
        self.boundaries = None
        self.island = None

        # Statistic variables
        self.get_stat = False
        self.surface_elem = None
        self.surface_elem_max = None
        self.surface_elem_min = None
        self.len_edge = None
        self.len_edge_min = None
        self.len_edge_max = None
        self.angle = None
        self.angle_min = None
        self.angle_max = None
        self.angle_stat = None
        self.ratio_edge = None
        self.nb_val_ratio_edge = None

        # Variable for MemoryError
        self.chunck_size = 1

        # Variable for Probe
        self.elem2probe = None
        self.file2probe = None
        self.list_proc = []
        self.triang = []
        self.liste_pt = []
        self.liste_pt3D = []
        self.is_create_tri4probe = False
        self.is_elem2probe = False

        if mode == 'rb' or mode == 'r+b':
            for num_file in range(self.ncsize):
                self.read_header(num_file=num_file)
            if read_time:
                self.get_temps(pdt_variable=pdt_variable)

    def getEndianFromChar(self, f, nchar):
        """
        Automatic recuperation if it's big endian or little endian
        Args:
            f:
            nchar:

        Returns:

        """
        pointer = f.tell()
        l, c, chk = unpack('{}i{}si'.format(self.endian, nchar), f.read(4 + nchar + 4))
        if chk != nchar:
            self.endian = "<"
            f.seek(pointer)
            l, c, chk = unpack('{}i{}si'.format(self.endian, nchar), f.read(4 + nchar + 4))
        if l != nchar:
            print('... Cannot read ' + str(nchar) + ' characters from your binary file')
            print('     +> Maybe it is the wrong file format ?')
            sys.exit(1)
        f.seek(pointer)

    def getFloatTypeFromFloat(self, f, nfloat):
        """
        Check if the result is in simple or double precision
        Args:
            f:
            nfloat:

        Returns:

        """
        pointer = f.tell()
        ifloat = self.precision[1]
        cfloat = self.precision[0]
        l = unpack(self.endian + 'i', f.read(4))
        if l[0] != ifloat * nfloat:
            ifloat = 8
            cfloat = 'd'
            self.precision = ['d', 8]
        r = unpack('{}{}{}'.format(self.endian, nfloat, cfloat), f.read(ifloat * nfloat))
        chk = unpack('{}i'.format(self.endian), f.read(4))
        if l != chk:
            print('... Cannot read ' + str(nfloat) + ' floats from your binary file')
            print('     +> Maybe it is the wrong file format ?')
            sys.exit(1)
        f.seek(pointer)

    def open(self):
        """
        Open the result and check if this is a scalar result or parallel
        Returns:

        """
        if not self.paral:
            self.FILE.append(open(self.name[0], self.mode))
            self.file = self.FILE[0]
        else:
            name_res = '{}{}-{}'
            path, name_base = os.path.split(self.name[0])
            liste_fic = os.listdir(path)
            for elem in liste_fic:
                if name_base in elem and len(name_base) < len(elem):
                    self.ncsize = int(elem.replace(name_base, '').split('-')[0]) + 1
                    break
            if self.ncsize == 1:
                print('il n y a pas de resultat contenant {} dans le repertoire {}'.format(name_base, path))
                sys.exit()

            self.name = []
            for num_proc in range(self.ncsize):
                name = os.path.join(path,
                                    name_res.format(name_base,
                                                    str(self.ncsize - 1).zfill(self.size_num_paral),
                                                    str(num_proc).zfill(self.size_num_paral)))
                self.name.append(name)
                self.FILE.append(open(name, self.mode))
        self.taille_pdt_ = [None for num_proc in range(self.ncsize)]
        self.entete_ = [None for num_proc in range(self.ncsize)]
        self.NPOIN = [None for num_proc in range(self.ncsize)]
        self.NELEM = [None for num_proc in range(self.ncsize)]
        self.IKLE = [None for num_proc in range(self.ncsize)]
        self.IPOBO = [None for num_proc in range(self.ncsize)]
        self.X = [None for num_proc in range(self.ncsize)]
        self.Y = [None for num_proc in range(self.ncsize)]
        self.NPOIN2D = [None for num_proc in range(self.ncsize)]
        self.NELEM2D = [None for num_proc in range(self.ncsize)]
        self.IKLE2D = [None for num_proc in range(self.ncsize)]
        self.X2D = [None for num_proc in range(self.ncsize)]
        self.Y2D = [None for num_proc in range(self.ncsize)]
        self.NODE_AREA = [None for num_proc in range(self.ncsize)]
        self.NEIGHBORS = [None for num_proc in range(self.ncsize)]
        self.is_get_2d = [False for num_proc in range(self.ncsize)]
        self.M = [None for num_proc in range(self.ncsize)]

    def read_header(self, num_file=0):
        """
        Read the header of the file
        Args:
            num_file:

        Returns:

        """
        self.FILE[num_file].seek(0, 0)
        # Recuperation du nombre d'octet dans le fichier
        self.taille_fichier = os.path.getsize(self.name[num_file])

        # Verification si c'est du big endian ou little endian
        self.getEndianFromChar(self.FILE[num_file], 80)
        # Lecture du titre
        num = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]  # debut encadrement
        self.title = self.FILE[num_file].read(num).decode('utf-8')
        self.FILE[num_file].read(4)  # fin encadrement

        # Lecture de nbvar et de nbvar2
        num = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]  # debut encadrement
        self.nbvar = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]  # nbvar
        self.nbvar2 = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]  # nbvar2
        self.FILE[num_file].read(4)  # fin encadrement

        # Lecture du nom des variables
        self.nomvar = []
        for j in range(self.nbvar):
            num = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]  # debut encadrement
            nomvar_tempo = self.FILE[num_file].read(num).decode('utf-8')
            self.FILE[num_file].read(4)  # fin encadrement
            self.nomvar.append(nomvar_tempo)
            if (nomvar_tempo.lower() in Serafin.nomvar2d[3].lower()
                    or nomvar_tempo.lower() in Serafin.nomvar2d_ENG[3]):
                self.FindH = True
                self.PosH = j
            elif (nomvar_tempo.lower() in Serafin.nomvar2d[4].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar2d_ENG[4].lower()):
                self.PosSL = j
            elif (nomvar_tempo.lower() in Serafin.nomvar2d[5].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar2d_ENG[5].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar3d[0].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar3d_ENG[0].lower()):
                self.PosZ = j
            elif (nomvar_tempo.lower() in Serafin.nomvar2d[0].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar2d_ENG[0].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar3d[1].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar3d_ENG[1].lower()):
                self.PosU = j
            elif (nomvar_tempo.lower() in Serafin.nomvar2d[1].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar2d_ENG[1].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar3d[2].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar3d_ENG[2].lower()):
                self.PosV = j
            elif (nomvar_tempo.lower() in Serafin.nomvar3d[3].lower()
                  or nomvar_tempo.lower() in Serafin.nomvar3d_ENG[3].lower()):
                self.PosW = j

        # Verification si date dans resultat
        num = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]
        self.date = unpack('{}10i'.format(self.endian), self.FILE[num_file].read(40))
        self.date = list(self.date)
        self.FILE[num_file].read(4)  # fin encadrement
        if (self.date[-1] == 1):
            # Lecture des 6 entier (si date)
            num = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]
            self.date_supp = unpack('{}6i'.format(self.endian), self.FILE[num_file].read(6 * 4))
            try:
                self.date_ref = datetime.datetime(*self.date_supp)
            except ValueError:
                self.date_ref = datetime.datetime(1970, 1, 1, 0, 0, 0)
            self.FILE[num_file].read(4)

        # Lecture des 4 entier nelem, npoin, ndp et i
        num = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]  # debut encadrement

        self.NELEM[num_file] = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]

        self.NPOIN[num_file] = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]

        self.ndp = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]

        # lecture du point i qui ne nous interesse pas
        self.var_i = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]
        self.FILE[num_file].read(4)  # fin encadrement

        # On ignore ikle
        num = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]  # debut encadrement
        nb_val = '{}{}i'.format(self.endian, self.NELEM[num_file] * self.ndp)
        self.IKLE[num_file] = np.array(unpack(nb_val, self.FILE[num_file].read(4 * self.NELEM[num_file] * self.ndp)))
        self.FILE[num_file].read(4)  # fin encadrement

        # On ignore IPOBO
        num = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]  # debut encadrement
        nb_val = '{}{}i'.format(self.endian, self.NPOIN[num_file])
        self.IPOBO[num_file] = np.array(unpack(nb_val, self.FILE[num_file].read(4 * self.NPOIN[num_file])))
        self.FILE[num_file].read(4)  # fin encadrement

        # On ignore x
        self.getFloatTypeFromFloat(self.FILE[num_file], self.NPOIN[num_file])
        num = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]  # debut encadrement
        nb_val = '{}{}{}'.format(self.endian, self.NPOIN[num_file], self.precision[0])
        self.X[num_file] = np.array(unpack(nb_val, self.FILE[num_file].read(self.precision[1] * self.NPOIN[num_file])))
        self.FILE[num_file].read(4)  # fin encadrement

        # On ignore y
        num = unpack('{}i'.format(self.endian), self.FILE[num_file].read(4))[0]  # debut encadrement
        self.Y[num_file] = np.array(unpack(nb_val, self.FILE[num_file].read(self.precision[1] * self.NPOIN[num_file])))
        self.FILE[num_file].read(4)  # fin encadrement

        # Recherche de la taille de l'entete
        self.entete_[num_file] = (80 + 8) + (8 + 8) + (self.nbvar * (8 + 32)) + (40 + 8) + (self.date[-1] * ((6 * 4) + 8)) + \
            (16 + 8) + ((int(self.NELEM[num_file]) * self.ndp * 4) + 8) + (self.NPOIN[num_file] * 4 + 8) + \
            (2 * (int(self.NPOIN[num_file]) * self.precision[1] + 8))
        self.entete = self.entete_[0]
        self.pos_fic = self.entete

        # Recherche de la taille de l'enregistrement (combien d'octet pour un PDT)
        self.taille_pdt_[num_file] = (8 + self.precision[1]) + (self.nbvar *
                                                                (8 + self.NPOIN[num_file] * self.precision[1]))
        self.taille_pdt = self.taille_pdt_[0]

        # Recuperation du nombre de PDT
        self.nb_pdt = int((self.taille_fichier - self.entete_[num_file]) / self.taille_pdt_[num_file])
        if num_file == 0:
            self.x = self.X[num_file]
            self.y = self.Y[num_file]
            self.ikle = self.IKLE[num_file]
            self.nelem = self.NELEM[num_file]
            self.ipobo = self.IPOBO[num_file]
            self.npoin = self.NPOIN[num_file]

    def pos_var(self, list_var):
        """
        Find the position for all variable given in the list "list_var". If the element is an integer
        don't change anything, if it's a string then find the position of the corresponding variable
        Args:
            list_var: list

        Returns:

        """
        for num_elem, elem in enumerate(list_var):
            if isinstance(elem, str):
                for num_name, name in enumerate(self.nomvar):
                    if elem.lower() in name.lower():
                        list_var[num_elem] = num_name
                        break
            elif isinstance(elem, int):
                None
            else:
                sys.exit("error in the type of the value in 'list_var'\n"
                         "it can be an integer or a string")

    def get_temps(self, pdt_variable=False, num_file=0):
        """
        Get the list of all time in the result
        If the time step is constant, we only read the 3 first value of time and reconstruct the total list of time (use
        the size of the file). If the time step are variable then we read the hole file
        Args:
            pdt_variable:
            num_file:

        Returns:

        """
        val = '{}{}'.format(self.endian, self.precision[0])
        if not pdt_variable:
            if self.nb_pdt < 3:
                for num_time in range(self.nb_pdt):
                    self.FILE[num_file].seek(self.entete_[num_file] + 4 + num_time * self.taille_pdt_[num_file], 0)
                    self.temps.append(unpack(val, self.FILE[num_file].read(self.precision[1]))[0])
            else:
                t = []
                for num_time in range(3):
                    self.FILE[num_file].seek(self.entete_[num_file] + 4 + num_time * self.taille_pdt_[num_file], 0)
                    t.append(unpack(val, self.FILE[num_file].read(self.precision[1]))[0])
                self.temps.append(t[0])
                for i in range(self.nb_pdt - 1):
                    self.temps.append(t[1] + i * (t[2] - t[1]))
        else:
            # Recuperation de tous les pas de temps
            self.temps = []
            # On se positionne a la fin de l'entete du fichier (debut des PDT)
            self.FILE[num_file].seek(self.entete_[num_file], 0)
            for num_time in range(self.nb_pdt):
                self.FILE[num_file].seek(4, 1)
                self.temps.append(unpack(val, self.FILE[num_file].read(self.precision[1]))[0])
                self.FILE[num_file].seek(self.taille_pdt_[num_file] - (self.precision[1] + 4), 1)
        self.temps = np.array(self.temps)

        # On se positionne a la fin de l'entete du fichier (debut des PDT)
        self.FILE[num_file].seek(self.entete_[num_file], 0)

    def get_info(self, num_file=0):
        """
        Get some info of the mesh:
        - Get the smallest and the largest element
        - Get the smallest and the largest edge
        - Get the total surface of the model

        :return:
        """
        ikle2 = np.reshape(self.IKLE[num_file], (self.NELEM[num_file], -1))
        for i in range(self.NELEM[num_file]):
            L1 = ((self.X[num_file][ikle2[i][0] - 1] - self.X[num_file][ikle2[i][1] - 1]) ** 2 + (
                self.Y[num_file][ikle2[i][0] - 1] - self.Y[num_file][ikle2[i][1] - 1]) ** 2) ** .5
            L2 = ((self.X[num_file][ikle2[i][1] - 1] - self.X[num_file][ikle2[i][2] - 1]) ** 2 + (
                self.Y[num_file][ikle2[i][1] - 1] - self.Y[num_file][ikle2[i][2] - 1]) ** 2) ** .5
            L3 = ((self.X[num_file][ikle2[i][0] - 1] - self.X[num_file][ikle2[i][2] - 1]) ** 2 + (
                self.Y[num_file][ikle2[i][0] - 1] - self.Y[num_file][ikle2[i][2] - 1]) ** 2) ** .5
            if min(L1, L2, L3) < self.min_elem:
                self.min_elem = min(L1, L2, L3)
            if max(L1, L2, L3) > self.max_elem:
                self.max_elem = max(L1, L2, L3)
            p = (L1 + L2 + L3) / 2
            Surface_elem = (p * (p - L1) * (p - L2) * (p - L3)) ** .5
            if Surface_elem < self.min_surface:
                self.min_surface = Surface_elem
            if Surface_elem > self.max_surface:
                self.max_surface = Surface_elem

            self.surface += Surface_elem

    def copy_info(self, resname, num_file=0):
        """
        Copy all info of a result to another
        :param resname:
        :return:
        """
        self.title = resname.title
        self.nbvar = resname.nbvar
        self.nbvar2 = resname.nbvar2
        self.nomvar = copy.deepcopy(resname.nomvar)
        self.date = copy.deepcopy(resname.date)
        self.date_supp = copy.deepcopy(resname.date_supp)
        self.nelem = resname.nelem
        self.npoin = resname.npoin
        self.ndp = resname.ndp
        self.var_i = resname.var_i
        self.ikle = copy.deepcopy(resname.ikle)
        self.ipobo = copy.deepcopy(resname.ipobo)
        self.x = copy.deepcopy(resname.x)
        self.y = copy.deepcopy(resname.y)
        self.entete_ = copy.deepcopy(resname.entete_)
        self.entete = resname.entete_[num_file]
        self.taille_pdt_ = copy.deepcopy(resname.taille_pdt_)  # [num_file]
        self.taille_pdt = resname.taille_pdt_[num_file]
        self.nb_pdt = resname.nb_pdt
        self.taille_fichier = resname.taille_fichier

        self.FindH = resname.FindH
        self.PosH = resname.PosH
        self.PosSL = resname.PosSL
        self.PosZ = resname.PosZ
        self.temps = resname.temps

    def write_header(self, num_file=0):
        """
        Write the header of the telemac result in the file
        :return:
        """
        # Lecture du titre
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 80))  # debut encadrement
        self.FILE[num_file].write(bytes(self.title, 'utf-8') + b' ' * (80 - len(self.title)))
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 80))  # fin encadrement

        # Lecture de nbvar et de nbvar2
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 2 * 4))  # debut encadrement
        self.FILE[num_file].write(pack('{}i'.format(self.endian), self.nbvar))  # nbvar
        self.FILE[num_file].write(pack('{}i'.format(self.endian), self.nbvar2))  # nbvar2
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 2 * 4))  # fin encadrement

        # Lecture du nom des variables
        for j in range(self.nbvar):
            self.FILE[num_file].write(pack('{}i'.format(self.endian), 32))  # debut encadrement
            self.FILE[num_file].write(bytes(self.nomvar[j], 'utf-8') + b' ' * (32 - len(self.nomvar[j])))
            self.FILE[num_file].write(pack('{}i'.format(self.endian), 32))  # fin encadrement

        # Verification si date dans resultat
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 10 * 4))  # debut encadrement
        self.FILE[num_file].write(pack('{}10i'.format(self.endian), *self.date))
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 10 * 4))  # fin encadrement
        if (self.date[-1] == 1):
            # Lecture des 6 entier (si date)
            self.FILE[num_file].write(pack('{}i'.format(self.endian), 6 * 4))  # debut encadrement
            self.FILE[num_file].write(pack('{}6i'.format(self.endian), *self.date_supp))
            self.FILE[num_file].write(pack('{}i'.format(self.endian), 6 * 4))  # fin encadrement

        # Lecture des 4 entier nelem, npoin, ndp et i
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * 4))  # debut encadrement
        self.FILE[num_file].write(pack('{}i'.format(self.endian), self.nelem))
        self.FILE[num_file].write(pack('{}i'.format(self.endian), self.npoin))
        self.FILE[num_file].write(pack('{}i'.format(self.endian), self.ndp))
        self.FILE[num_file].write(pack('{}i'.format(self.endian), self.var_i))
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * 4))  # fin encadrement

        # On ecrit ikle
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.nelem * self.ndp))  # debut encadrement
        try:
            nb_val = '{}{}i'.format(self.endian, self.nelem * self.ndp)
            self.FILE[num_file].write(pack(nb_val, *self.ikle.flatten()))
        except MemoryError:
            self.memory_error(self.nelem, self.ndp, self.ikle)

        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.nelem * self.ndp))  # fin encadrement

        # On ecrit IPOBO
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.npoin))  # debut encadrement
        nb_val = '{}{}i'.format(self.endian, self.npoin)
        try:
            self.FILE[num_file].write(pack(nb_val, *self.ipobo))
        except MemoryError:
            self.memory_error(self.npoin, 1, self.ipobo)
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.npoin))  # fin encadrement

        # On ecrit x
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.npoin))  # debut encadrement
        nb_val = '{}{}{}'.format(self.endian, self.npoin, self.precision[0])
        try:
            self.FILE[num_file].write(pack(nb_val, *self.x))
        except MemoryError:
            self.memory_error(self.npoin, 1, self.x)

        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.npoin))  # fin encadrement

        # On ecrit y
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.npoin))  # debut encadrement
        try:
            self.FILE[num_file].write(pack(nb_val, *self.y))
        except MemoryError:
            self.memory_error(self.npoin, 1, self.y)
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.npoin))  # fin encadrement

    def read(self, time2read, var2del=[], is_time=True, specific_frame=False, num_file=0):
        """
        Read all the value of a specific time (or a specifc position of time)
        :param time2read:
        :param var2del:
        :param is_time:
        :param specific_frame:
        :return:
        """
        taille_pdt = np.array([self.taille_pdt_[num_file]], dtype=np.int64)
        if is_time:
            pos_time2read = np.where(self.temps == time2read)[0][0]
        else:
            pos_time2read = time2read

        if not specific_frame:
            pos_actu = np.int64(self.entete_[num_file] + pos_time2read * taille_pdt[0] + (8 + self.precision[1]))
            self.FILE[num_file].seek(pos_actu, 0)
            self.pos_pdt = pos_time2read + 1
        else:
            self.FILE[num_file].seek(self.entete_[num_file], 0)
            for num_time in range(pos_time2read):
                self.FILE[num_file].seek(self.taille_pdt_[num_file], 1)
                self.pos_pdt = num_time + 1
            self.FILE[num_file].seek(8 + self.precision[1], 1)

        nb_val = '{}{}{}'.format(self.endian, self.NPOIN[num_file], self.precision[0])
        var = []
        for pos_var in range(self.nbvar):
            self.FILE[num_file].read(4)
            var.append(unpack(nb_val, self.FILE[num_file].read(self.precision[1] * self.NPOIN[num_file])))
            self.FILE[num_file].read(4)

        var = np.array(var)

        if len(var2del) > 0:
            var = np.delete(var, var2del, 0)

        return var

    # @profile
    def all_time_node(self, pos_node, time2read=None, var2keep=None, num_file=0):
        """
        read all time for a specific node
        :param pos_node:
        :param time2read:
        :param var2keep:
        :return:
        """
        if time2read is not None:
            pos_time2read = np.where(self.temps == time2read)[0][0]
        else:
            pos_time2read = range(0, len(self.temps))

        if var2keep is not None:
            None
        else:
            var2keep = range(self.nbvar)

        precision = self.precision[1]
        octet_pos_node = [(8 + precision * self.NPOIN[num_file]) * num_var + 4 + pos_node * precision for num_var, name in
                          enumerate(self.nomvar)]
        taille_pdt_var = self.taille_pdt_[num_file] - (8 + precision)

        res = np.zeros((self.nbvar, len(self.temps)))
        nb_val = '{}{}{}'.format(self.endian, 1, self.precision[0])

        # Close the file and reopen it. It avoid doing a seek on a large file
        for num_time, val in enumerate(pos_time2read):
            pos_actu = np.int64(self.entete_[num_file] + val * self.taille_pdt_[num_file] + (8 + precision))
            offset = np.int64(np.int64(pos_actu / mmap.ALLOCATIONGRANULARITY) * mmap.ALLOCATIONGRANULARITY)
            remain_octet = np.int64(np.int64(pos_actu) - np.int64(offset))
            mm = mmap.mmap(self.FILE[num_file].fileno(),
                           remain_octet + taille_pdt_var,
                           access=mmap.ACCESS_READ,
                           offset=offset)
            for num_var, name_var in enumerate(self.nomvar):
                if num_var in var2keep:
                    first = remain_octet + octet_pos_node[num_var]
                    last = first + precision
                    res[num_var, num_time] = unpack(nb_val, mm[first:last])[0]
        mm.close()

        return res

    def read_nodes(self, time2read, liste_nodes, var2del=[],
                   is_time=True, continuous_time=False, valech=1,
                   num_file=0):
        """
        Read just a list of node instead of reading all node of the result
        :param time2read:
        :param liste_nodes:
        :param var2del:
        :param is_time:
        :return:
        """
        taille_pdt = np.array([self.taille_pdt_[num_file]], dtype=np.int64)
        if continuous_time:
            if self.first_continuous:
                self.first_continuous = False
                if is_time:
                    pos_time2read = np.where(self.temps == time2read)[0][0]
                else:
                    pos_time2read = time2read
                pos_actu = self.entete_[num_file] + taille_pdt[0] * pos_time2read + 8 + self.precision[1]
                self.pos_pdt = pos_time2read
            else:
                self.pos_pdt += valech
                pos_actu = self.entete_[num_file] + taille_pdt[0] * self.pos_pdt + 8 + self.precision[1]
        else:
            if is_time:
                pos_time2read = np.where(self.temps == time2read)[0][0]
            else:
                pos_time2read = time2read

            try:
                pos_actu = np.int64(self.entete_[num_file] + pos_time2read * taille_pdt[0] + (8 + self.precision[1]))
                self.FILE[num_file].seek(np.int64(self.entete_[num_file] + pos_actu), 0)
            except Warning:
                print('WARNING IN READ_NODES')
                self.FILE[num_file].seek(self.entete_[num_file], 0)
                for num_time in range(pos_time2read):
                    self.FILE[num_file].seek(taille_pdt[0], 1)
                    self.pos_pdt = num_time + 1
                self.FILE[num_file].seek(8 + self.precision[1], 1)
            except IOError:
                print('ERROR IN READ_NODES')
                if self.first_error:
                    self.first_error = False
                    self.FILE[num_file].seek(self.entete_[num_file], 0)
                    for num_time in range(pos_time2read):
                        self.FILE[num_file].seek(taille_pdt[0], 1)
                        self.pos_pdt = num_time + 1
                else:
                    self.FILE[num_file].seek(taille_pdt[0], 1)
                self.FILE[num_file].seek(8 + self.precision[1], 1)
                # pos_actu = self.entete + taille_pdt[0] * pos_time2read + 8 + self.precision[1]
        offset = int(pos_actu / mmap.ALLOCATIONGRANULARITY) * \
            mmap.ALLOCATIONGRANULARITY
        remain_octet = pos_actu - offset
        mm = mmap.mmap(self.FILE[num_file].fileno(),
                       remain_octet + (self.precision[1] * self.NPOIN[num_file] + 8) * self.nbvar,
                       access=mmap.ACCESS_READ,
                       offset=offset)

        nb_val = '{}{}{}'.format(self.endian, len(liste_nodes), self.precision[0])
        var = []
        for pos_var in range(self.nbvar):
            first = remain_octet + (4 + self.precision[1] * self.NPOIN[num_file] + 4) * pos_var + 4
            last = remain_octet + (4 + self.precision[1] * self.NPOIN[num_file] + 4) * (pos_var + 1) - 4
            val_tempo = mm[first:last]
            val = b''.join(val_tempo[i:i + self.precision[1]] for i in liste_nodes)
            var.append(unpack(nb_val, val))

        mm.close()

        var = np.array(var)

        # Force the garbage collector
        gc.collect()
        return var

    def write_frame(self, time, var, num_file=0):
        """
        write in the result all the variable for the corresponding time
        :param time:
        :param var:
        :return:
        """
        if len(var) != self.nbvar:
            erreur = "Il n'y a pas le meme nombre de variable entre la taille de var et nbvar\n\
                      Le nombre de variable attendu est de {nbvar}, alors \
                      que la dimension de l'enregistrement est de {shape}".format(nbvar=self.nbvar, shape=var.shape)
            raise Exception(erreur)
        nb_val = '{}{}{}'.format(self.endian, self.npoin, self.precision[0])
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4))
        self.FILE[num_file].write(pack('{}{}'.format(self.endian, self.precision[0]), time))
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4))
        for val_var in var:
            self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.npoin))
            try:
                self.FILE[num_file].write(pack(nb_val, *val_var))
            except MemoryError:
                self.memory_error(self.npoin, 1, val_var)
            self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.npoin))

    def write_value(self, val_var, num_file=0):
        """
        write in the result only one variable in the result
        :param val_var:
        :return:
        """
        nb_val = '{}{}{}'.format(self.endian, self.npoin, self.precision[0])
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.npoin))
        try:
            self.FILE[num_file].write(pack(nb_val, *val_var))
        except MemoryError:
            self.memory_error(self.npoin, 1, val_var)
        self.FILE[num_file].write(pack('{}i'.format(self.endian), 4 * self.npoin))

    def get_2d(self, num_file=0):
        """
        Get the 2D value (coordinates, ikle ...)
        :return:
        """
        self.nplan = self.date[6]
        for num_file in range(self.ncsize):
            if self.nplan > 1:
                self.NPOIN2D[num_file] = int(self.NPOIN[num_file] / self.nplan)
                self.NELEM2D[num_file] = int(self.NELEM[num_file] / (self.nplan - 1))
                self.IKLE2D[num_file] = self.IKLE[num_file] - 1
                self.IKLE2D[num_file] = self.IKLE2D[num_file].reshape((self.NELEM[num_file], 6))
                self.IKLE2D[num_file] = self.IKLE2D[num_file][:self.NELEM2D[num_file], :3]
                self.X2D[num_file] = self.X[num_file][:self.NPOIN2D[num_file]]
                self.Y2D[num_file] = self.Y[num_file][:self.NPOIN2D[num_file]]
            else:
                self.NPOIN2D[num_file] = self.NPOIN[num_file]
                self.NELEM2D[num_file] = self.NELEM[num_file]
                self.IKLE2D[num_file] = self.IKLE[num_file] - 1
                self.IKLE2D[num_file] = self.IKLE2D[num_file].reshape((self.NELEM[num_file], 3))
                self.X2D[num_file] = self.X[num_file]
                self.Y2D[num_file] = self.Y[num_file]
            self.is_get_2d[num_file] = True
        self.npoin2d = self.NPOIN2D[num_file]
        self.nelem2d = self.NELEM2D[num_file]
        self.ikle2d = self.IKLE2D[num_file]
        self.x2d = self.X2D[num_file]
        self.y2d = self.Y2D[num_file]
        self.node_area = self.NODE_AREA[num_file]
        # Force the garbage collector
        gc.collect()

    def in_triangulation(self, points, num_file=0):
        """
        For each node, find the corresponding node (if exists)
        :param points:
        :return:
        """
        import matplotlib.tri as tri

        if not self.is_get_2d[num_file]:
            self.get_2d(num_file=num_file)

        triang = tri.Triangulation(self.X2D[num_file], self.Y2D[num_file], self.IKLE2D[num_file])
        x, y = zip(*points)
        try:
            findtri = triang.get_trifinder()
            res_elem = findtri(x, y)
        except RuntimeError:
            from scipy import spatial
            tree = spatial.KDTree(zip(self.X2D[num_file], self.Y2D[num_file]))
            neighbor = tree.query(points, k=10)
            res_elem = np.zeros(len(points), dtype=int)
            res_elem.fill(-1)
            for idx, (xi, yi) in enumerate(points):
                is_find = False
                for idx2, num_pt in enumerate(neighbor[1][idx]):
                    liste_all_elem = np.where(self.IKLE2D[num_file] == num_pt)[0]
                    x1 = self.X2D[num_file][self.IKLE2D[num_file][liste_all_elem]]
                    y1 = self.Y2D[num_file][self.IKLE2D[num_file][liste_all_elem]]
                    for idx3, (x_tri, y_tri) in enumerate(zip(x1, y1)):
                        v0 = [x_tri[-1] - x_tri[0],
                              y_tri[-1] - y_tri[0]]
                        v1 = [x_tri[1] - x_tri[0],
                              y_tri[1] - y_tri[0]]
                        v2 = [xi - x_tri[0],
                              yi - y_tri[0]]
                        dot00 = v0[0] * v0[0] + v0[1] * v0[1]
                        dot01 = v0[0] * v1[0] + v0[1] * v1[1]
                        dot02 = v0[0] * v2[0] + v0[1] * v2[1]
                        dot11 = v1[0] * v1[0] + v1[1] * v1[1]
                        dot12 = v1[0] * v2[0] + v1[1] * v2[1]
                        invDenom = 1. / (dot00 * dot11 - dot01 * dot01)
                        u = (dot11 * dot02 - dot01 * dot12) * invDenom
                        v = (dot00 * dot12 - dot01 * dot02) * invDenom
                        if (u >= 0.) and (v >= 0.) and ((u + v) < 1.):
                            res_elem[idx] = liste_all_elem[idx3]
                            is_find = True
                            break
                    if is_find:
                        break
        # Force the garbage collector
        gc.collect()
        return np.array(res_elem)

    def area_for_node(self, num_file=0):
        """
        Find the area for each node of the mesh
        We use the Barycentric option
        :return:
        """

        if not self.is_get_2d[num_file]:
            self.get_2d(num_file=num_file)

        self.NODE_AREA[num_file] = np.zeros(self.NPOIN2D[num_file], dtype=float)
        xa, ya = self.X2D[num_file][self.IKLE2D[num_file][:, 0]], self.Y2D[num_file][self.IKLE2D[num_file][:, 0]]
        xb, yb = self.X2D[num_file][self.IKLE2D[num_file][:, 1]], self.Y2D[num_file][self.IKLE2D[num_file][:, 1]]
        xc, yc = self.X2D[num_file][self.IKLE2D[num_file][:, 2]], self.Y2D[num_file][self.IKLE2D[num_file][:, 2]]
        xap, yap = (xc + xb) / 2., (yc + yb) / 2.
        xbp, ybp = (xa + xc) / 2., (ya + yc) / 2.
        xcp, ycp = (xa + xb) / 2., (ya + yb) / 2.
        xg = 1. / 3. * (xa + xb + xc)
        yg = 1. / 3. * (ya + yb + yc)
        a1 = .5 * (xa * ycp - ya * xcp +
                   xcp * yg - ycp * xg +
                   xg * ybp - yg * xbp +
                   xbp * ya - ybp * xa)
        a2 = .5 * (xb * yap - yb * xap +
                   xap * yg - yap * xg +
                   xg * ycp - yg * xcp +
                   xcp * yb - ycp * xb)
        a3 = .5 * (xc * ybp - yc * xbp +
                   xbp * yg - ybp * xg +
                   xg * yap - yg * xap +
                   xap * yc - yap * xc)
        a1 = np.abs(a1)
        a2 = np.abs(a2)
        a3 = np.abs(a3)
        for idx, (a, b, c) in enumerate(self.IKLE2D[num_file]):
            self.NODE_AREA[num_file][a] += a1[idx]
            self.NODE_AREA[num_file][b] += a2[idx]
            self.NODE_AREA[num_file][c] += a3[idx]
        self.node_area = self.NODE_AREA[num_file]
        # Force the garbage collector
        # gc.collect()

    def stat_mesh(self,
                  angle_min=0, angle_max=10,
                  num_file=0):
        """
        Return static for the mesh
        :return:
        """
        import math

        if not self.is_get_2d[num_file]:
            self.get_2d(num_file=num_file)

        xa, ya = self.X2D[num_file][self.IKLE2D[num_file][:, 0]], self.Y2D[num_file][self.IKLE2D[num_file][:, 0]]
        xb, yb = self.X2D[num_file][self.IKLE2D[num_file][:, 1]], self.Y2D[num_file][self.IKLE2D[num_file][:, 1]]
        xc, yc = self.X2D[num_file][self.IKLE2D[num_file][:, 2]], self.Y2D[num_file][self.IKLE2D[num_file][:, 2]]
        len_ab = np.power(np.power(xa - xb, 2.) + np.power(ya - yb, 2.), 0.5)
        len_ac = np.power(np.power(xa - xc, 2.) + np.power(ya - yc, 2.), 0.5)
        len_bc = np.power(np.power(xb - xc, 2.) + np.power(yb - yc, 2.), 0.5)
        self.len_edge = np.array([list(len_ab), list(len_ac), list(len_bc)])

        angle_abc = np.arccos((np.power(len_ab, 2.) + np.power(len_ac, 2.) - np.power(len_bc, 2.)) / (
            2 * len_ab * len_ac)) * 180. / math.pi
        angle_acb = np.arccos((np.power(len_bc, 2.) + np.power(len_ac, 2.) - np.power(len_ab, 2.)) / (
            2 * len_bc * len_ac)) * 180. / math.pi
        angle_bac = np.arccos((np.power(len_ab, 2.) + np.power(len_bc, 2.) - np.power(len_ac, 2.)) / (
            2 * len_ab * len_bc)) * 180. / math.pi
        self.angle = np.array([list(angle_abc), list(angle_acb), list(angle_bac)])

        s = 0.5 * (len_ab + len_bc + len_ac)
        self.surface_elem = np.power(s * (s - len_ab) * (s - len_ac) * (s - len_bc), 0.5)

        self.surface_elem_max = np.amax(self.surface_elem)
        self.surface_elem_min = np.amin(self.surface_elem)

        self.len_edge_min = np.amin(self.len_edge)
        self.len_edge_max = np.amax(self.len_edge)

        self.angle_min = np.amin(self.angle)
        self.angle_max = np.amax(self.angle)
        self.angle_stat = []
        angle_min, angle_max = 1, 10
        for idx in range(angle_min, angle_max):
            ind = np.argwhere(((np.amin(self.angle, axis=0) < idx) & (np.amin(self.angle, axis=0) >= idx - 1)))
            if len(ind) > 0:
                self.angle_stat.append([len(ind), list(np.transpose(ind)[0] + 1)])
            else:
                self.angle_stat.append([0, -1])
        ind = np.argwhere(np.amin(self.angle, axis=0) > angle_max)
        if len(ind) > 0:
            self.angle_stat.append([len(ind), list(np.transpose(ind)[0] + 1)])
        else:
            self.angle_stat.append([0, -1])

        self.ratio_edge = np.amax(self.len_edge, axis=0) / np.amin(self.len_edge, axis=0)

        self.nb_val_ratio_edge = []
        for idx in range(1, 10):
            ind = np.argwhere(((self.ratio_edge < idx) & (self.ratio_edge >= idx - 1)))
            if len(ind) > 0:
                self.nb_val_ratio_edge.append([len(ind), list(np.transpose(ind)[0] + 1)])
            else:
                self.nb_val_ratio_edge.append([0, -1])
        ind = np.argwhere(((self.ratio_edge < idx) & (self.ratio_edge >= 10)))
        if len(ind) > 0:
            self.nb_val_ratio_edge.append([len(ind), list(np.transpose(ind)[0] + 1)])
        else:
            self.nb_val_ratio_edge.append([0, -1])

        self.get_stat = True
        # Force the garbage collector
        # gc.collect()

    def find_voisin(self):
        """
        Get all neighbour of a node
        :return:
        """
        import pandas as pd
        from scipy.sparse import csr_matrix

        for num_file in range(self.ncsize):
            if not self.is_get_2d[num_file]:
                self.get_2d(num_file=num_file)
            if self.M[num_file] is None:
                cols = np.arange(self.IKLE2D[num_file].size)
                self.M[num_file] = csr_matrix((cols, (self.IKLE2D[num_file].ravel(), cols)),
                                              shape=(self.IKLE2D[num_file].max() + 1, self.IKLE2D[num_file].size))
            self.NEIGHBORS[num_file] = [np.unique(self.IKLE2D[num_file][np.unravel_index(row.data, self.IKLE2D[num_file].shape)[
                                                  0]].ravel()) for idx, row in enumerate(self.M[num_file])]
            self.neighbors_tri = [np.unravel_index(row.data, self.IKLE2D[num_file].shape)[0]
                                  for idx, row in enumerate(self.M[num_file])]
            for idx, val in enumerate(self.NEIGHBORS[num_file]):
                self.NEIGHBORS[num_file][idx] = val[val != idx]
            df = pd.DataFrame(self.NEIGHBORS[num_file])
            self.NEIGHBORS[num_file] = np.array(df.fillna(-1).values, dtype=int)

    def find_corresp_seg(self, num_file=0):
        """
        find for each segment, the corresponding elements
        :return:
        """
        import matplotlib.tri as tri
        from collections import Counter

        if not self.is_get_2d[num_file]:
            self.get_2d(num_file=num_file)

        self.find_voisin()
        triang = tri.Triangulation(self.X2D[num_file], self.Y2D[num_file], self.IKLE2D[num_file])
        edges = triang.edges

        self.edges_corresp = []
        for idx, (e1, e2) in enumerate(edges):
            tempo = []
            tempo.extend(np.unravel_index(self.M[num_file][e1].data, self.IKLE2D[num_file].shape)[0])
            tempo.extend(np.unravel_index(self.M[num_file][e2].data, self.IKLE2D[num_file].shape)[0])
            self.edges_corresp.append([k for k, v in Counter(tempo).items() if v > 1])
            self.dico_edges['{};{}'.format(min(e1, e2), max(e1, e2))] = idx
        # Force the garbage collector
        # gc.collect()

    def find_tri_by_edge(self, n1, n2, num_file=0):
        """
        User give the 2 node number of an edge and we find the corresponding triangle
        :param n1: node 1
        :param n2: node 2
        :return: list of triangle
        """
        from scipy.sparse import csr_matrix
        from collections import Counter

        for num_file in range(self.ncsize):
            if not self.is_get_2d[num_file]:
                self.get_2d(num_file=num_file)
            if self.M[num_file] is None:
                cols = np.arange(self.IKLE2D[num_file].size)
                self.M[num_file] = csr_matrix((cols, (self.IKLE2D[num_file].ravel(), cols)),
                                              shape=(self.IKLE2D[num_file].max() + 1, self.IKLE2D[num_file].size))
            tempo = []
            tempo.extend(np.unravel_index(self.M[num_file][n1].data, self.IKLE2D[num_file].shape)[0])
            tempo.extend(np.unravel_index(self.M[num_file][n2].data, self.IKLE2D[num_file].shape)[0])
        # Force the garbage collector
        # gc.collect()

        return [k for k, v in Counter(tempo).items() if v > 1]

    def find_boundaries(self, num_file=0):
        """
        Find all boundaries in the mesh (not working in parallel mode)
        Returns:

        """
        if self.NEIGHBORS[num_file] is None:
            self.find_voisin()
        ptfr = np.where(self.IPOBO[num_file] > 0)[0]
        list_boundaries_node = self.IPOBO[num_file][ptfr]
        idx_b = np.argsort(list_boundaries_node)
        ptfr = ptfr[idx_b]
        first_pt = ptfr[0]
        pos_front = 0
        self.boundaries_node = []
        self.boundaries = []
        self.island = []
        for idx, num_fr in enumerate(ptfr):
            if pos_front == 0:
                self.boundaries_node.append([])
                self.boundaries_node[-1].append(num_fr)
                pos_front += 1
            elif pos_front < 3:
                self.boundaries_node[-1].append(num_fr)
                pos_front += 1
            else:
                self.boundaries_node[-1].append(num_fr)
                pos_front += 1
                if first_pt in self.NEIGHBORS[num_file][num_fr]:
                    # if (idx + 1) < len(ptfr) and ptfr[idx+1] not in self.neighbors[num_fr]:
                    #     pos_front=0
                    #     if idx<len(ptfr)-1:
                    #         first_pt=ptfr[idx+1]
                    pos_front = 0
                    if idx < len(ptfr) - 1:
                        first_pt = ptfr[idx + 1]
        from shapely.geometry.polygon import LinearRing
        for idx, val in enumerate(self.boundaries_node):
            tempo = LinearRing(np.transpose((self.X[num_file][val], self.Y[num_file][val])))
            if not tempo.is_ccw:
                self.island.append(tempo)
            else:
                self.boundaries.append(tempo)
        # Force the garbage collector
        # gc.collect()

    def get_elem2probe(self, xysonde, num_file=0):
        """
        Fonction permettant de recuperer tous les fichiers resultats necessaire
        a l'execution du point sonde.
        Si le calcul n'est pas recompose, alors recuperationd des resultats ou se trouve
        les points sondes et stockage de l'element associe a chaque point sonde.
        Parametre d'entree:
        - xysonde (list) : coordonnee des points sondes en (x,y)
        Parametre de sortie:
        -
        fonctions appelees:
        - aucune

        """
        self.is_elem2probe = True
        self.elem2probe = np.zeros((self.ncsize, len(xysonde)), dtype=int)
        self.elem2probe.fill(-1)

        if not self.paral:
            res_elem = self.in_triangulation(xysonde)
            for idx, elem in enumerate(res_elem):
                if elem > -1:
                    self.elem2probe[0, idx] = elem
            self.list_proc.append(0)
        else:
            for num_proc in range(self.ncsize):
                res_elem = self.in_triangulation(xysonde, num_file=num_proc)
                for idx, elem in enumerate(res_elem):
                    if elem > -1:
                        self.elem2probe[num_proc, idx] = elem
            for num_pt in range(len(xysonde)):
                index = np.where(self.elem2probe[:, num_pt] > -1)[0]
                if len(index) > 1:
                    self.elem2probe[:, num_pt][index[1:]] = -1
            self.list_proc = []
            for num_proc in range(self.ncsize):
                index = np.where(self.elem2probe[num_proc, :] > -1)[0]
                if len(index) > 0:
                    self.list_proc.append(num_proc)

    def create_tri4probe(self):
        """
        This programm create a new triangulation for fast probe and also get all the node to read
        Returns:

        """
        # Suppression des elements qui sont en doublons
        self.is_create_tri4probe = True
        if not self.paral:
            elem_unique = list(set(self.elem2probe[0]))
            if -1 in elem_unique:
                elem_unique.remove(-1)
            elem_unique = [elem_unique]
        else:
            elem_unique = []
            for num_proc in range(self.ncsize):
                elem_unique.append(list(set(self.elem2probe[num_proc])))
                if -1 in elem_unique[-1]:
                    elem_unique[-1].remove(-1)
        # Creation de notre triangulation pour interpolation
        self.nplan = self.date[6]
        if self.nplan == 0:
            self.nplan = 1
        for idx, num_proc in enumerate(self.list_proc):
            if not self.is_get_2d[idx]:
                self.get_2d(num_file=idx)
            ikle_tri = self.IKLE2D[num_proc][elem_unique[num_proc], :]
            self.liste_pt.append(np.unique(ikle_tri))
            # Renumerotation de la triangulation pour debuter à 0
            for idx, val in enumerate(ikle_tri):
                ikle_tri[idx, 0] = np.where(self.liste_pt[-1] == val[0])[0]
                ikle_tri[idx, 1] = np.where(self.liste_pt[-1] == val[1])[0]
                ikle_tri[idx, 2] = np.where(self.liste_pt[-1] == val[2])[0]
            x_tri = self.X2D[num_proc][self.liste_pt[-1]]
            y_tri = self.Y2D[num_proc][self.liste_pt[-1]]
            self.triang.append(tri.Triangulation(x_tri, y_tri, ikle_tri))
            self.liste_pt3D.append([])
            for num_z in range(self.nplan):
                for elem2 in self.liste_pt[-1]:
                    self.liste_pt3D[-1].append((num_z * self.NPOIN2D[num_proc] + elem2) * self.precision[1])

    def probe(self, xysonde, list_var, time, option3d={'code': 1}):
        """
        Probe the Serafin file given a list of couple (x,y) at a specific time for a list
        of variables
        Args:
            time:
            var:
            xysonde:

        Returns:

        """
        if not self.is_elem2probe:
            self.get_elem2probe(xysonde)
        if not self.is_create_tri4probe:
            self.create_tri4probe()
        if not self.paral:
            var = self.read_nodes(time, self.liste_pt3D[0],
                                  continuous_time=False)
            res = self.interp_val(var, xysonde, self.triang[0], list_var,
                                  len(self.liste_pt[0]), option3d=option3d)
        else:
            res = np.zeros((self.nplan, len(list_var), len(xysonde)))
            for idx, num_proc in enumerate(self.list_proc):
                index = np.where(self.elem2probe[num_proc, :] > -1)[0]
                var = self.read_nodes(time, self.liste_pt3D[idx],
                                      continuous_time=False, num_file=num_proc)
                res[:, :, index] = self.interp_val(var, xysonde[index], self.triang[idx], list_var,
                                                   len(self.liste_pt[idx]), option3d=option3d)

        return res

    def interp_val(self, var, xysonde, triang, list_var, npoin2d, option3d={'code': 1}):
        """

        Args:
            var:
            nb_z:
            xysonde:
            triang:
            list_var:
            npoin2d:
            option3d:

        Returns:

        """
        xsonde, ysonde = zip(*xysonde)
        if option3d is None or option3d['code'] == 1:
            res = np.zeros((self.nplan, len(list_var), len(xysonde)))
            for num_z in range(self.nplan):
                for idx, val in enumerate(list_var):
                    interp = tri.LinearTriInterpolator(triang,
                                                       var[val][npoin2d * num_z: npoin2d * (num_z + 1)])
                    res[num_z, idx, :] = interp(xsonde, ysonde)
        else:
            if option3d['code'] == 0:
                res = np.zeros((len(option3d['valeurs']), len(list_var), len(xysonde)))
                res_tempo = np.zeros((self.nplan, len(list_var), len(xysonde)))
                val_z = np.zeros((self.nplan, len(xsonde)))
                for num_z in range(self.nplan):
                    interp_z = tri.LinearTriInterpolator(triang,
                                                         var[self.PosZ][npoin2d * num_z: npoin2d * (num_z + 1)])
                    val_z[num_z, :] = interp_z(xsonde, ysonde)
                    for idx, val in enumerate(list_var):
                        interp = tri.LinearTriInterpolator(triang,
                                                           var[val][npoin2d * num_z: npoin2d * (num_z + 1)])
                        res_tempo[num_z, idx, :] = interp(xsonde, ysonde)
                for idx_var in range(len(list_var)):
                    for idx_sonde in range(len(xsonde)):
                        res[:, idx_var, idx_sonde] = np.interp(option3d['valeurs'],
                                                               val_z[:, idx_sonde],
                                                               res_tempo[:, idx_var, idx_sonde])
        return res

    def close(self):
        """
        Close all file
        Returns:

        """
        for file in self.FILE:
            file.close()

    def memory_error(self, dimension1_var, dimension2, var):
        try:
            if self.chunck_size > 10000000:
                raise(MemoryError)
            if self.chunck_size == 1:
                self.chunck_size *= 10

            val_diviseur = int(dimension1_var / self.chunck_size)
            val_left = dimension1_var - (val_diviseur * self.chunck_size)
            if isinstance(var, list):
                for i in range(self.chunck_size):
                    nb_val = '{}{}i'.format(self.endian, val_diviseur * dimension2)
                    val_tempo = var[i * val_diviseur: (i + 1) * val_diviseur]
                    self.FILE[0].write(pack(nb_val, *val_tempo))
                if val_left > 0:
                    nb_val = '{}{}i'.format(self.endian, val_left * dimension2)
                    val_tempo = var[-val_left:]
                    self.FILE[0].write(pack(nb_val, *val_tempo))
            else:
                for i in range(self.chunck_size):
                    nb_val = '{}{}i'.format(self.endian, val_diviseur * dimension2)
                    val_tempo = var[i * val_diviseur: (i + 1) * val_diviseur].flatten()
                    self.FILE[0].write(pack(nb_val, *val_tempo))
                if val_left > 0:
                    nb_val = '{}{}i'.format(self.endian, val_left * dimension2)
                    val_tempo = var[-val_left:].flatten()
                    self.FILE[0].write(pack(nb_val, *val_tempo))
        except MemoryError:
            self.chunck_size *= 10
            self.memory_error(dimension1_var, dimension2, var)
