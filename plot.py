import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
# plt.style.use('ggplot')
from pandas import  read_csv
import os.path
import logging
logging.basicConfig(level=logging.INFO)

def plot(name, trajectory, S = []):

    fig = plt.figure()
    plt.xlabel("lat")
    plt.ylabel("lon")
    plt.axis('equal')
    

    ax = fig.add_subplot(111)
    
    x = [p['x'] for p in trajectory]
    y = [p['y'] for p in trajectory]

    ax.plot(x,y, '-')
    
    
    if len(S) != 0:
        trajectory_simplified = [trajectory[i] for i in S]
        sx = [p['x'] for p in trajectory_simplified]
        sy = [p['y'] for p in trajectory_simplified]
        ax.plot(sx,sy, 'ro--')
    
    fig.savefig(str(name)+'.png')

def plot_bar_file(fin, yLabel, xLabel='k'):
    InPath = 'result/'
    Outpath = 'fig/'
    
    size = 15
    
    if not os.path.isfile(InPath+fin):
        logging.error("File: "+ InPath+fin+" is not exist.")
        return
    
    df = read_csv(InPath+fin, index_col = 0) #dataframe type  
    
    # print df
    ax = df.plot(kind='bar', rot=0, color = 'w', legend=False, fontsize=size)

    
    patches, labels = ax.get_legend_handles_labels()
    
    bars = ax.patches
    hatches = ''.join(h*len(df) for h in 'x/O.')

    for bar, hatch in zip(bars, hatches):   # plot hatch
        bar.set_hatch(hatch)
    
    # ax.legend(patches, labels, loc='upper center', bbox_to_anchor=(0.5, 1.25), fontsize=20, ncol = 3, frameon=False)
    # ax.legend(patches, labels, loc=0, fontsize=18, ncol = 1)
    
    plt.xlabel(xLabel, fontsize=size)
    plt.ylabel(yLabel, fontsize=size)
    plt.savefig(Outpath+fin[:-4]+'.jpg')
    
def plot_line_file(fin, yLabel, xLabel='k'):
    InPath = 'result/'
    Outpath = 'fig/'
    
    if not os.path.isfile(InPath+fin):
        logging.error(" "+ InPath+fin+" is not exist.")
        return
        
    
    df = read_csv(InPath+fin, index_col = 0) #dataframe type  
    
    fSize = 20
    
    # print df
    # ax = df.plot(kind='line', legend=False, rot=0) markerfacecolor='none', markeredgewidth=1.5
    ax = df.plot(kind='line', rot=0, markersize=15,  style=['-o', '-s', '--v', '--^', '-.D', '-.H'], legend=False, fontsize=fSize, linewidth=1.5) # black
    # ax = df.plot(kind='line', rot=0, markersize=20, markerfacecolor='none', style=['-o', '-s', '-v', '-^', '-D'], legend=False, fontsize=fSize, linewidth=2.0) # color
    
    patches, labels = ax.get_legend_handles_labels()
    
    
    # bars = ax.patches
    # hatches = ''.join(h*len(df) for h in 'x/O.')

    # for bar, hatch in zip(bars, hatches):   # plot hatch
        # bar.set_hatch(hatch)
    
    # ax.legend(patches, labels, loc='upper center', bbox_to_anchor=(0.5, 1.13), ncol=3)
    ax.legend(patches, labels, loc=4, fontsize=fSize, numpoints = 1 )
    
    plt.xlabel(xLabel, fontsize=fSize)
    plt.ylabel(yLabel, fontsize=fSize)
    plt.savefig(Outpath+fin[:-4]+'.jpg')