Name:           cycle
Version:        0.3.2
Release:        1%{?dist}
Summary:        Calendar program for women
Group:          Applications/Productivity
License:        GPLv2+
URL:            http://moggers.co.uk/cgit/cycle.git/about/
Source0:        http://moggers.co.uk/cgit/cycle.git/snapshot/cycle-%{version}.tar.bz2
Source1:        cycle.desktop
BuildArch:      noarch
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Requires:       wxPython
BuildRequires:  python-devel >= 2.3, gettext,desktop-file-utils

%description
Cycle is a calendar for women. Given a cycle length or statistics
for several periods, it can calculate the days until
menstruation, the days of "safe" sex, the fertile period, and the
days to ovulations, and define the d.o.b. of a child. It allows
the user to write notes and helps to supervise the administration
of hormonal contraceptive tablets.

Multiple users allowed. Data is protected by a password for every
user.

NOTE: This program is not a reliable contraceptive method. It
does neither help to prevent sexual transmision diseases like
AIDS. It is just an electronic means of keeping track of some of
your medical data and extract some statistical conclusions from
them. You cannot consider this program as a substitute for your
gynecologist in any way.

%prep
%setup -q

%build
python setup.py build
make -C msg
#---- set_dir.py ----
cat >set_dir.py <<EOF
#generated from cycle.spec
msg_dir="%_datadir/locale"
doc_dir="%_docdir/%name-%version"
icons_dir="%_iconsdir"
bitmaps_dir="%_datadir/%name/bitmaps"
EOF

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT

install -p -m a+rx,u+w -d \
    $RPM_BUILD_ROOT%{_datadir}/cycle/{pixmaps,bitmaps}
install -p -m a+r,u+w icons/cycle.xpm \
    $RPM_BUILD_ROOT%{_datadir}/cycle/pixmaps/
install -p -m a+r,u+w bitmaps/* $RPM_BUILD_ROOT%{_datadir}/cycle/bitmaps/
install -p -m a+rx,u+w -d \
    $RPM_BUILD_ROOT%{_datadir}/cycle/icons/{large,mini}
cp -r -p icons/* $RPM_BUILD_ROOT%{_datadir}/cycle/icons/
install -p -m a+rx,u+w -d $RPM_BUILD_ROOT%{_datadir}/applications/
install -p -m a+r,u+w %{SOURCE1} \
    $RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop

# Python libraries
install -p -m a+rx,u+w cycle.py $RPM_BUILD_ROOT%{_datadir}/cycle/
install -p -m a+r,u+w cal_year.py dialogs.py p_rotor.py \
    save_load.py set_dir.py \
    $RPM_BUILD_ROOT%{_datadir}/cycle/

# cycle binary
install -p -m a+rx,u+w -d $RPM_BUILD_ROOT%{_bindir}
ln -sf ../share/cycle/cycle.py $RPM_BUILD_ROOT%{_bindir}/cycle
make -C msg install DESTDIR=$RPM_BUILD_ROOT%{_datadir}/

# manpage
install -p -m a+rx,u+w -d \
    $RPM_BUILD_ROOT%{_mandir}/man1/
install -p -m a+r,u+w cycle.1 $RPM_BUILD_ROOT%{_mandir}/man1/

desktop-file-install \
--dir $RPM_BUILD_ROOT%{_datadir}/applications \
--vendor=fedora \
--delete-original \
$RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop
%find_lang %{name} || touch %{name}.lang

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root,-)
%{_bindir}/cycle
%doc README* COPYRIGHT CHANGELOG THANKS
%{_datadir}/cycle/
%{_datadir}/applications/fedora-cycle.desktop
%{_mandir}/man1/cycle*


%changelog
* Fri Nov 25 2011 Matt Molyneaux <moggers87+git@moggers87.co.uk> - 0.3.2-1
- New upstream

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.1-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Aug 11 2010 David Malcolm <dmalcolm@redhat.com> - 0.3.1-10
- recompiling .py files against Python 2.7 (rhbz#623284)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Dec 01 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.3.1-7
- Rebuild for Python 2.6

* Tue Jul 15 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.3.1-6
- fix license tag

* Fri May  4 2007 Matej Cepl <mcepl@redhat.com> - 0.3.1-5
- added information about source of Debian files.

* Tue Apr  3 2007 Matej Cepl <mcepl@redhat.com> - 0.3.1-4
- changed BuildRoot to more sane value, now it is allowed.

* Thu Feb  1 2007 Matěj Cepl <mcepl@redhat.com> 0.3.1-3
- don't gzip manpage -- rpmbuild does it automagically
- category should be Application/Productivity (or
  non-Productivity in this case, but that's not included into RH
  standards :-))
- generate set_dir.py (according to the upstream .spec file)
- fixed cs.po

* Wed Jan 31 2007 Matěj Cepl <mcepl@redhat.com> 0.3.1-2
- fixed missing files in %%doc
- fixed Description
- added manpage
- fixed .desktop file

* Sat Jan 6 2007 Matěj Cepl <mcepl@redhat.com> 0.3.1-1
- Initial build based on Debian package cycle_0.3.1-6
