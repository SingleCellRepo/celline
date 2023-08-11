for file in $(find . -type f -name "*.py" ! -name "__init__.py"); do
    nuitka3 --module $file
done

for dir in $(find . -type d); do
    if [[ -f $dir/__init__.py ]]; then
        nuitka3 --module $dir
    fi
done

scons