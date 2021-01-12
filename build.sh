#! /usr/bin/env bash
#
# Build Debian package in a Docker container
#

# Get build platform as 1st argument, and collect project metadata
image="${1:?You MUST provide a docker image name}"; shift
dist_id=${image%%:*}
codename=${image#*:}
#pypi_name="$(./setup.py --name)"
pypi_name="mipqctool"
pkgname="$(dh_listpackages)"
tag=$pypi_name-$dist_id-$codename
staging_dir="build/staging"

# Prepare staging area
rm -rf $staging_dir 2>/dev/null || true
mkdir -p $staging_dir
git ls-files >build/git-files
test ! -f .npmrc || echo .npmrc >>build/git-files
tar -c --files-from build/git-files | tar -C $staging_dir -x
sed -i -r -e 1s/stretch/$codename/g $staging_dir/debian/changelog
sed -r -e s/#UUID#/$(< /proc/sys/kernel/random/uuid)/g \
    -e s/#DIST_ID#/$dist_id/g -e s/#CODENAME#/$codename/g \
    -e s/#NODEREPO#/$NODEREPO/g -e s/#PYPI#/$pypi_name/g -e s/#PKGNAME#/$pkgname/g \
    <Dockerfile.build >$staging_dir/Dockerfile
cp dh-virtualenv-build-deps_1.2.2-1_all.deb $staging_dir/dh-virtualenv-build-deps_1.2.2-1_all.deb
cp dh-virtualenv_1.2.2-1~bionic_all.deb $staging_dir/dh-virtualenv_1.2.2-1~bionic_all.deb
# Build in Docker container, save results, and show package info
docker build --tag $tag "$@" $staging_dir
docker run --rm $tag tar -C /dpkg -c . | tar -C build -xv
dpkg-deb -I build/${pkgname}_*~${codename}*.deb