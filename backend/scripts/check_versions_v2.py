import pkg_resources
import sys

def check_versions():
    packages = ['xhtml2pdf', 'reportlab', 'html5lib', 'pisa']
    with open('versions_installed.txt', 'w') as f:
        f.write(f"Python Version: {sys.version}\n\n")
        f.write("--- Installed Packages ---\n")
        for p in packages:
            try:
                version = pkg_resources.get_distribution(p).version
                f.write(f"{p}: {version}\n")
            except pkg_resources.DistributionNotFound:
                f.write(f"{p}: NOT INSTALLED\n")
            except Exception as e:
                f.write(f"{p}: Error checking - {str(e)}\n")

if __name__ == "__main__":
    check_versions()
    print("Versions written to versions_installed.txt")
