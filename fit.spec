# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}


%define section free

Summary:        Framework for Integrated Test
Name:           fit
Version:        1.1
Release:        %mkrel 1.0.5
Epoch:          0
License:        GPL
URL:            http://fit.c2.com/
Group:          Development/Java
Source0:        http://prdownloads.sourceforge.net/fit/fit-java-1.1.zip
Patch0:         fit-1.1-build_xml.patch
BuildRequires:  ant
BuildRequires:  ant-junit
BuildRequires:  java-rpmbuild >= 0:1.6
BuildRequires:  junit
%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
%endif
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Great software requires collaboration and communication.
Fit is a tool for enhancing collaboration in software
development. It's an invaluable way to collaborate on
complicated problems--and get them right--early in development.
Fit allows customers, testers, and programmers to learn what
their software should do and what it does do. It automatically
compares customers' expectations to actual results. 

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
Requires(post):   /bin/rm,/bin/ln
Requires(postun): /bin/rm

%description javadoc
%{summary}.

%package manual
Summary:        Documents for %{name}
Group:          Development/Java

%description manual
%{summary}.

%prep
%setup -c -q -n %{name}-%{version}
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
%patch0 -b .sav
%{_bindir}/find . -name '*.css' -o -name '*.html' -o -name '*.txt' | \
  %{_bindir}/xargs -t %{__perl} -pi -e 's/\r$//g'
%{__perl} -pi -e 's/fork="true"/fork="false"/g' source/imp/java/build.xml

%build
export CLASSPATH=$(build-classpath junit):`pwd`/source/imp/java/output/jars/fit.jar
export OPT_JAR_LIST="ant/ant-junit"
pushd source/imp/java
# XXX: %{ant} release fails with gcj so spec, examples, and test targets are disabled
# XXX: Permission (java.lang.RuntimePermission exitVM) was not granted.
# XXX: http://developer.classpath.org/pipermail/classpath-patches/2007-May/005469.html
%if %{gcj_support}
%{ant} build jars javadoc
%else
%{ant} release
%endif
popd

%install
rm -rf $RPM_BUILD_ROOT

# jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}

install -m 0644 source/imp/java/output/jars/%{name}.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -a source/imp/java/doc/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}
rm -rf source/imp/java/doc/api

# manual
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -a source/imp/java/doc/* $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}
%endif

%if %{gcj_support}
%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%doc license.txt
%{_javadir}/*.jar
%if %{gcj_support}
%attr(-,root,root) %dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-%{version}.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%files manual
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}
