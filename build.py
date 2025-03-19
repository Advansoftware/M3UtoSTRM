import os
import subprocess
import shutil
import sys

def build_frontend():
    """Build do frontend Next.js"""
    os.chdir('frontend')
    print("Building Next.js frontend...")
    # Build Next.js com exportação estática
    subprocess.run('npm run build', shell=True, check=True)
    # Copiar a pasta .next/static para dist/static
    os.makedirs('dist', exist_ok=True)
    if os.path.exists('.next/static'):
        shutil.copytree('.next/static', 'dist/static', dirs_exist_ok=True)
    os.chdir('..')

def build_executable():
    """Build do executável usando PyInstaller"""
    print("Building executable...")
    if sys.platform == 'win32':
        subprocess.run('pyinstaller m3utostrm.spec --clean', shell=True, check=True)
    else:
        # No Linux, usar o script de build_windows.sh para cross-compilation
        subprocess.run('bash build_windows.sh', shell=True, check=True)

def main():
    # Limpar builds anteriores
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    try:
        # Build do frontend
        build_frontend()
        
        # Build do executável
        build_executable()
        
        print("Build completed successfully!")
        
    except Exception as e:
        print(f"Error during build: {str(e)}")

if __name__ == "__main__":
    main()
