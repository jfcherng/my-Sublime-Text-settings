#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


#---------#
# configs #
#---------#

TEMP_DIR=".Sublime-Official-Packages"
PKG_GITHUB_URL="https://github.com/sublimehq/Packages"
PKG_REMOTE_REPO="${PKG_GITHUB_URL}.git"

ST_INSTALL_DIRS=(
    # this script's dir and its parent
    "${SCRIPT_DIR}"
    "${SCRIPT_DIR}/.."
    # Windows
    "C:/Program Files/Sublime Text"
    "C:/Program Files/Sublime Text 3"
    # Linux
    "/opt/sublime_text"
    "/opt/sublime_text_3"
    # Mac
    "/Applications/Sublime Text.app/Contents/MacOS"
    "/Applications/Sublime Text 3.app/Contents/MacOS"
)


#-----------#
# functions #
#-----------#

pushd() {
    # suppress messages from pushd, which is usually verbose
    command pushd "$@" > /dev/null
}

popd() {
    # suppress messages from popd, which is usually verbose
    command popd > /dev/null
}


#-------#
# begin #
#-------#

pushd "${SCRIPT_DIR}" || exit

rm -rf "${TEMP_DIR}" && mkdir -p "${TEMP_DIR}"

pushd "${TEMP_DIR}" || exit


#-------------------------------------------#
# try to find the ST installation directory #
#-------------------------------------------#

paths_to_check=(
    "Packages/"
    "changelog.txt"
)

for st_install_dir in "${ST_INSTALL_DIRS[@]}"; do
    st_install_dir="${st_install_dir%/}"

    is_passed=1
    for path_to_check in "${paths_to_check[@]}"; do
        path_to_check="${st_install_dir}/${path_to_check}"

        # if the path under checking is a dir, it ends with a slash
        if [[ "${path_to_check}" =~ /$ ]]; then
            if [ ! -d "${path_to_check}" ]; then
                is_passed=0
                break
            fi
        else
            if [ ! -f "${path_to_check}" ]; then
                is_passed=0
                break
            fi
        fi
    done

    if [ "${is_passed}" = "1" ]; then
        echo "[INFO][V] ST installation directory: '${st_install_dir}'"
        break
    else
        echo "[INFO][X] ST installation directory: '${st_install_dir}'"
        st_install_dir=""
    fi
done

if [ "${st_install_dir}" = "" ]; then
    echo "[ERROR] Cannot find the ST installation directory..."
    exit 1
fi

st_pkgs_dir="${st_install_dir}/Packages"


#----------------------------#
# read option: branch_or_tag #
#----------------------------#

echo "[INFO] You could check branches/tags on '${PKG_GITHUB_URL}/releases'"
read -erp "Branch or tag to be used (such as 'v3152', default = 'master'): " branch_or_tag

if [ "${branch_or_tag}" = "" ]; then
    branch_or_tag="master"
fi

if [[ "${branch_or_tag}" =~ ^[0-9]+$ ]]; then
    branch_or_tag="v${branch_or_tag}"
fi


#-------------------------------#
# get the latest package source #
#-------------------------------#

repo_dir="repo"

rm -rf "${repo_dir}"

echo "[INFO] Downloading repository..."

git clone --depth=1 --branch="${branch_or_tag}" "${PKG_REMOTE_REPO}" "${repo_dir}"

if [ $? -eq 0 ]; then
    echo "[INFO] Download repository successfully!"
else
    echo "[Error] Fail to checkout the branch/tag '${branch_or_tag}'..."
    exit 1
fi


#------------------#
# pack up packages #
#------------------#

packed_pkgs_dir="packages"

mkdir -p "${packed_pkgs_dir}"

pushd "${repo_dir}" || exit

echo "[INFO] Pack up packages..."

# traverse all packages in the repo
for dir in */; do
    pushd "${dir}" || exit

    pkg_name=${dir%/}

    echo "[INFO] Packaging '${pkg_name}'..."

    zip -9rq "../../${packed_pkgs_dir}/${pkg_name}.sublime-package" .

    popd || exit
done

popd || exit


#------------------#
# replace packages #
#------------------#

echo "[INFO] Update ST packages to ${branch_or_tag}..."
command cp -rf "${packed_pkgs_dir}"/*.sublime-package "${st_pkgs_dir}"


#----------#
# clean up #
#----------#

popd || exit

echo "[INFO] Clean up..."
rm -rf "${TEMP_DIR}"


#-----#
# end #
#-----#

popd || exit
