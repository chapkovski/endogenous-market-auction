from termcolor import colored
import shutil
from shutil import copyfile


def cp(*x, color='red', center=True):
    columns = shutil.get_terminal_size().columns
    x = ' '.join([str(i) for i in x])
    if center:
        x = x.center(columns, '-')
    print(colored(x, color, 'on_cyan', attrs=['bold']))

# TODO: move to management
def create_templates():
    from volauction.pages import page_sequence
    path = 'volauction/templates/volauction/'
    for p in page_sequence:
        copyfile(f'{path}MyPage.html', f'{path}{p.__name__}.html')