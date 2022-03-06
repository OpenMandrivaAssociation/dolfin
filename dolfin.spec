#define _disable_ld_no_undefined 1

Summary:	A computational backend of FEniCS and implementation of the FEniCS Problem Solving Environment
Name:		dolfin
Version:	2019.1.0.post0
Release:	1
License:	LGPLv3+
Group:		Sciences/Mathematics
URL:		https://fenicsproject.org
Source0:	https://bitbucket.org/fenics-project/dolfin/downloads/%{name}-%{version}.tar.gz
# (fedora)
#Patch0:	%{name}-2019.1.0-fix-pkgconfig.patch

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	gcc-gfortran
BuildRequires:	gnupg2
BuildRequires:  blas-devel
BuildRequires:	boost-devel
BuildRequires:	eigen3-devel
BuildRequires:	hdf5-devel
# unpackaged
#BuildRequires:	petsc-devel
BuildRequires:	sundials-devel
BuildRequires:	scotch-devel
BuildRequires:  zlib-devel
BuildRequires:  python3-devel
BuildRequires:	pybind11-devel
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(fenics-ffc) >= %{fenics_version}
BuildRequires:  python3dist(fenics-ufl) >= %{fenics_version}
BuildRequires:  python3dist(fenics-dijitso) >= %{fenics_version}

#BuildRequires:	suitesparse-devel
#BuildRequires:	scotch-devel
#BuildRequires:	vtk-devel #libvtk6-dev
#BuildRequires:	pkgconfig(libxml-2.0) #libxml2-dev
#BuildRequires:	mpi-devel #mpi-default-dev
#BuildRequires:	#petsc-dev
#BuildRequires:	#slepc-dev
#BuildRequires:	#python-petsc4py
#BuildRequires:	#python-slepc4py
#BuildRequires:	pkgconfig(python)
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
export PATH=%{_libdir}/openmpi/bin/:$PATH
export LDFLAGS="%ldflags -L%{_libdir}/openmpi/lib -lpython%{python3_version}"
#export CFLAGS="%{optflags} -Wno-unused-variable -L%{_libdir}/openmpi/lib"
#export CXXFLAGS="%{optflags} -L%{_libdir}/openmpi/lib"
%cmake -Wno-dev \
	-DBUILD_SHARED_LIBS:BOOL=ON \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DCMAKE_INSTALL_RPATH_USE_LINK_PATH:BOOL=OFF \
	-DDOLFIN_ENABLE_TRILINOS:BOOL=OFF \
	-DDOLFIN_ENABLE_MPI:BOOL=ON \
	-DCMAKE_INSTALL_RPATH_USE_LINK_PATH:BOOL=OFF \
	-DCMAKE_INSTALL_RPATH_USE_LINK_PATH:BOOL=OFF \
	-G Ninja
%ninja_build

# "temporary install" so the python build can find the stuff it needs
%ninja_install

pushd ../python
VERBOSE=1 CMAKE_PREFIX_PATH=%{buildroot}%{_datadir}/%{name}/cmake CMAKE_SKIP_INSTALL_RPATH=yes CMAKE_SKIP_RPATH=yes %py_build
popd

%install
%ninja_install -C build

# python
pushd ./python
VERBOSE=1 CMAKE_PREFIX_PATH=%{buildroot}%{_datadir}/%{name}/cmake CMAKE_SKIP_INSTALL_RPATH=yes CMAKE_SKIP_RPATH=yes %py_install
popd

# there's even an option for this, except it seems to have no effect
chrpath %{buildroot}%{python3_sitearch}/dolfin/*.so
chrpath --delete %{buildroot}%{python3_sitearch}/dolfin/*.so

# remove unwanted files
rm -fr %{buildroot}%{_datadir}/%{name}/%{name}.conf

