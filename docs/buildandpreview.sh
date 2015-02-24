if which -s sphinx-autobuild ; then
    echo "Using sphinx-autobuild in" $(which sphinx-autobuild)
    sphinx-build . _build && sphinx-autobuild . _build
else
    echo "You don't have sphinx-autobuild installed."
    echo "Install it with pip3 instal sphinx-autobuild."
fi
