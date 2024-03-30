%bcond_without	hdf5
%bcond_without	openmpi
%bcond_without	petsc
%bcond_without	scotch
%bcond_with		trillions
%bcond_without	zlib

Summary:	A computational backend of FEniCS and implementation of the FEniCS Problem Solving Environment
Name:		dolfin
Version:	2019.1.0.post0
Release:	6
License:	LGPLv3+
Group:		Sciences/Mathematics
URL:		https://fenicsproject.org
Source0:	https://bitbucket.org/fenics-project/dolfin/downloads/dolfin-%{version}.tar.gz
# (fedora)
#Patch0:	%{name}-2019.1.0-fix-pkgconfig.patch
Patch0:		https://src.fedoraproject.org/rpms/dolfin/raw/rawhide/f/0001-Add-missing-include-for-compatiblity-with-gcc-13.patch
Patch1:		https://src.fedoraproject.org/rpms/dolfin/raw/rawhide/f/0001-pkgconfig-drop-irrelevant-part-from-Libs-and-Cflags.patch

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	gcc-gfortran
BuildRequires:	gnupg2
BuildRequires:	boost-devel
BuildRequires:	eigen3-devel
%if %{with hdf5}
BuildRequires:	hdf5-devel
%endif
BuildRequires:	cmake(pybind11)
BuildRequires:	cmake(sundials)
BuildRequires:  pkgconfig(blas)
BuildRequires:	pkgconfig(libxml-2.0)
%if %{with openmpi}
BuildRequires:  pkgconfig(ompi)
%endif
%if %{with patsc}
BuildRequires:	pkgconfig(petsc)
%endif
%if %{with zlib}
BuildRequires:	pkgconfig(zlib)
%endif
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(fenics-dijitso)
BuildRequires:  python3dist(fenics-ufl)
BuildRequires:  python3dist(fenics-ffc)
%if %{with scotch}
BuildRequires:	scotch-devel
%endif
BuildRequires:  suitesparse-devel

#BuildRequires:	vtk-devel #libvtk6-dev

#BuildRequires:	#slepc-dev
#BuildRequires:	#python-petsc4py
#BuildRequires:	#python-slepc4py
#BuildRequires:	python3egg(ply)
#BuildRequires:	swig #swig3.0 (>= 3.0.3)


%description
DOLFIN is the computational backend of FEniCS and implements the FEniCS
Problem Solving Environment in Python and C++.

%files
%license COPYING COPYING.LESSER
%doc AUTHORS README.rst
%{_bindir}/%{name}-version
%{_bindir}/fenics-version
%{_libdir}/lib%{name}.so.*
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/data
%{_datadir}/%{name}/data/README

#--------------------------------------------------------------------

%package devel
Summary:	Developnet files fo Dolfin
Requires:	dolfin = %{EVRD}

%description devel
DOLFIN is the computational backend of FEniCS and implements the FEniCS
Problem Solving Environment in Python and C++.

This packages provides stuff for developers.

%files devel
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%{_includedir}//%{name}.h
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_datadir}/%{name}/cmake

#--------------------------------------------------------------------

%package -n python-%{name}
Summary:        Python wrapper for the FEniCS dolfin environment
Requires:       %{name}-devel = %{EVRD}
%{?python_provide:%python_provide python-%name}

%description -n python-%{name}
DOLFIN is the computational backend of FEniCS and implements the FEniCS
Problem Solving Environment in Python and C++.

This packages provides a pythonwrapper for dolfin.

%files -n python-%{name}
%{_bindir}/%{name}-convert
%{_bindir}/%{name}-order
%{_bindir}/%{name}-plot
%{py_platsitedir}/%{name}/*
%{py_platsitedir}/%{name}_utils/
%{py_platsitedir}/fenics/
%{py_platsitedir}/fenics_%{name}-*-py%{python_version}.egg-info/

#--------------------------------------------------------------------

%package doc
Summary:        Documentation and demos for %{name}
BuildArch:      noarch

%description doc
DOLFIN is the computational backend of FEniCS and implements the FEniCS
Problem Solving Environment in Python and C++.

This packages provides a documentation and demos for dolfin.

%files doc
%{_bindir}/%{name}-get-demos
%{_datadir}/%{name}/demo

#--------------------------------------------------------------------

%prep
%autosetup -p1

# Let's just specify an exact version of a dependency, yay!
sed -i -r 's|pybind11==|pybind11>=|' python/setup.py
 
cat >>python/CMakeLists.txt <<EOF
set(CMAKE_CXX_FLAGS "\${CMAKE_CXX_FLAGS} -I$PWD")
EOF
 
# https://bugzilla.redhat.com/show_bug.cgi?id=1843103
sed -r -i 's/#include </#include <algorithm>\n\0/' \
  dolfin/geometry/IntersectionConstruction.cpp \
  dolfin/mesh/MeshFunction.h
 
sed -r -i 's|boost/detail/endian.hpp|boost/endian/arithmetic.hpp|' \
  dolfin/io/VTKFile.cpp \
  dolfin/io/VTKWriter.cpp

%build
export PATH=$PATH:%{_libdir}/openmpi/bin/
export LDFLAGS="%ldflags -L%{_libdir}/openmpi/lib -lpython%{python3_version}"
export CFLAGS="%{optflags} -Wno-unused-variable -DH5_USE_110_API"
export CXXFLAGS="%{optflags} -DH5_USE_110_API"

# -- The following OPTIONAL packages have not been found:
#
#  * PETSc (required version >= 3.7), Portable, Extensible Toolkit for Scientific Computation, <https://www.mcs.anl.gov/petsc/>
#    Enables the PETSc linear algebra backend
#  * SUNDIALS (required version >= 3), SUite of Nonlinear and DIfferential/ALgebraic Equation Solvers, <http://computation.llnl.gov/projects/sundials>
#    Provides robust time integrators and nonlinear solvers that can easily be incorporated into existing simulation codes.
#  * SCOTCH, Programs and libraries for graph, mesh and hypergraph partitioning, <https://www.labri.fr/perso/pelegrin/scotch>
#    Enables parallel graph partitioning

%cmake -Wno-dev \
	-DBUILD_SHARED_LIBS:BOOL=ON \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DCMAKE_INSTALL_RPATH_USE_LINK_PATH:BOOL=OFF \
	-DDOLFIN_ENABLE_HDF5:BOOL=%{?with_hdf5:ON}%{?!with_hdf5:OFF} \
	-DDOLFIN_ENABLE_MPI:BOOL=%{?with_openmpi:ON}%{?!with_openmpi:OFF} \
	-DDOLFIN_ENABLE_PETSC:BOOL=%{?with_petsc:ON}%{?!with_petsc:OFF} \
	-DDOLFIN_ENABLE_SCOTCH:BOOL=%{?with_scotch:ON}%{?!with_scotch:OFF} \
	-DDOLFIN_ENABLE_TRILINOS:BOOL=%{?with_trillions:ON}%{?!with_trillions:OFF} \
	-DDOLFIN_ENABLE_ZLIB:BOOL=%{?with_zlib:ON}%{?!with_zlib:OFF} \
	-G Ninja
%ninja_build

# "temporary install" so the python build can find the stuff it needs
%ninja_install

pushd ../python
export CMAKE_PREFIX_PATH=%{buildroot}/usr/share/dolfin/cmake
export CMAKE_SKIP_INSTALL_RPATH=yes CMAKE_SKIP_RPATH=yes
%py_build
popd

%install
%ninja_install -C build

# python
pushd ./python
%py_install
popd

# there's even an option for this, except it seems to have no effect
chrpath %{buildroot}%{py_platsitedir}/dolfin/*.so
chrpath --delete %{buildroot}%{py_platsitedir}/dolfin/*.so

# remove unwanted files
rm -fr %{buildroot}%{_datadir}/%{name}/%{name}.conf

