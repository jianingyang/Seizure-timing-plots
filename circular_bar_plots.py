#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Compute the number of seizure episodes occuring during each time duration, default 1h.
def num_by_time(data, color, bin_size=60):
    num_bins = int(1440/bin_size)
    data_min = np.zeros(num_bins)
    for index, row in data.iterrows():
        data_min[int(row["StartTime(min)"]//bin_size)] += row["StartTime(min)"]//bin_size + 1 -row["StartTime(min)"]/bin_size
        data_min[int(row["StartTime(min)"]//bin_size+1): int((row["StartTime(min)"]+row["Duration(min)"])//bin_size+1)] += 1
        data_min[int((row["StartTime(min)"]+row["Duration(min)"])//bin_size+1) % num_bins] += (row["StartTime(min)"]+row["Duration(min)"])/bin_size - ((row["StartTime(min)"]+row["Duration(min)"])//bin_size)
    
    df = pd.DataFrame({"Episodes": data_min})
    df[["Name"]] = ""
    df[["Color"]] = color
    df['Color'] = df['Color'].apply(lambda x: tuple(ti/255 for ti in eval(x)))
    # Compute max and min in the dataset
    max = df['Episodes'].max()
    df[["Max"]] = max
    
    return df

def plot_circ_bar(df, title, n_groups=2):
    # set figure size
    plt.figure(figsize=(5,5))
    
    # plot polar axis
    ax = plt.subplot(111, polar=True)
    
    # remove grid
    plt.axis('off')

    plt.title(title)
    
    # Set the coordinates limits
    upperLimit = 100
    lowerLimit = 0
    
    # Compute the height of each bar
    # The maximum will be converted to the upperLimit (100)
    slope = (upperLimit - lowerLimit) / df.Max
    heights = slope * df.Episodes + lowerLimit
    
    # Compute the width of each bar. In total we have 2*Pi
    width = n_groups*2*np.pi / len(df.index)
    
    # Compute the angle each bar is centered on:
    indexes = range(1, len(df.index)+1)
    angles = [-(element -1) * width + np.pi/2 for element in indexes]
    angles
    
    # Draw bars
    bars = ax.bar(
        x=angles, 
        height=heights, 
        width=width, 
        bottom=lowerLimit,
        color=df.Color,
        alpha=0.3)
    
    # Add labels
    for bar, angle, height, label in zip(bars,angles, heights, df["Name"]):
        ax.text(
            x=angle, 
            y=upperLimit,
            s=label)

    plt.savefig(f"plots/{title}.tiff")

# Combine circular bar plots of different experimental groups into one plot for comparison.
def combined_plot(data, group_colors, title):
    list = []
    for group in group_colors:
        group_data = data.loc[data["GroupName"] == group[0]]
        group_min = num_by_time(group_data, group[1])
        list.append(group_min)
    
    df = pd.concat(list, ignore_index=True)
    
    plot_circ_bar(df, title, n_groups=len(group_colors))


from os import listdir
from os.path import isfile, join

files = [f for f in listdir("./") if isfile(join("./", f))] #filenames should contain the name and color of each group
filelist = sorted(files)[1:-1]

color_list = []
for name in filelist:
    string = name.split(" - ")[1].split(".")[0].split(", ")
    color_list.append([string[i].replace("(", '').replace(")", '').split(" ") for i in range(len(string))])

for i in range(len(filelist)):
    data = pd.read_excel(filelist[i], header=1)
    
    data[["StartTime(min)"]] = data[["ZTStartTime"]]*60
    
    group_colors = color_list[i]
    
    combined_plot(data, group_colors, filelist[i].split('.')[0])

