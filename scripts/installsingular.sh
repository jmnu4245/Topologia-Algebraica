#!/bin/bash

# 1. Instalar dependencias y la versión de Singular del repositorio base de Ubuntu
sudo apt-get update
sudo apt-get install -y singular python3 python3-pip

# 2. Instalar Jupyter y el kernel de Singular
pip3 install --user jupyter jupyter_kernel_singular

# 3. Aplicar el parche permanente para el módulo obsoleto 'imghdr'
find ~/.local/lib/python*/site-packages/jupyter_kernel_singular/ -type f -name "*.py" -exec sed -i 's/import imghdr/class imghdr: what = lambda *a, **kw: "png"/g' {} +

# 4. Asegurar que la ruta de binarios locales de Python esté en el PATH
export PATH=$PATH:~/.local/bin
if ! grep -q 'export PATH=$PATH:~/.local/bin' ~/.bashrc; then
    echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
fi

# 5. Comprobación final
echo "--------------------------------------------------------"
jupyter kernelspec list
echo "--------------------------------------------------------"
echo "Si la instalación ha ido bien, 'singular' debería aparecer en la lista de arriba."