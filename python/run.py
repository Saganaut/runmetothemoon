# image rec to get score
# sendkey to mimic key input
# genetic algo to make key presses
import sys
import pyscreenshot as ImageGrab
from pytesser import *
from PIL import Image
import time
import winkeys
import os
import csv 
import random

#win key codes
keys_dict = {'q':0x10, 'w':0x11, 'o':0x18, 'p':0x19, 'space':0x39, 'r':0x13}
muta_dict = {0:'p', 1:'p', 2:'w', 3:'q'}
generations = 10000

def get_score(top=False):
	if top:
		im=ImageGrab.grab(bbox=(500,320,730,375))
		im.save('out.bmp')
	else:
		im=ImageGrab.grab(bbox=(540,495,700,520)) # X1,Y1,X2,Y2
	stringy = image_to_string(im)

	# pieces = stringy.split(" ")
	mgone =  stringy[0:stringy.find("m")]
	try:
		score = float(mgone.replace(" ", ""))
	except ValueError:
		return None
	print score
	return score

def done_yet():
	test_im=ImageGrab.grab(bbox=(500,500,501,501)) # X1,Y1,X2,Y2
	rgb_im = test_im.convert('RGB')
	r, g, b = rgb_im.getpixel((0, 0))
	if r == 237 and g == 237 and b == 237: #237s finish screen
		return True
	return False
	

def test_individual(genome):
	print genome
	c = 0
	n = len(genome)
	start = time.time()
	while True:
		if c % 20 == 0:
			if done_yet():
				break;
		winkeys.hit_key(keys_dict[genome[c%n]], 0.1)
		c+=1
		if c > 250:
			score = get_score(True) 
			print "stuck, resetting:"
			winkeys.hit_key(keys_dict['r'], 0.1)
			return score
	score = get_score()
	return score

def start_simulation():
	base_str = "../data/gen"
	c = 0
	last_viable_gen = 0
	while os.path.isfile(base_str+str(c)):
		c+=1
	c-=1
	pool = populate_species_from_file(base_str+str(c))
	#evaluate current pool
	for i in range(5,1,-1):
		time.sleep(1)
		print i
	current_genomes = set()
	for g in range(c,generations):
		current_genomes.clear()
		map(lambda x: current_genomes.add(x[0]), pool)
		for s in range(len(pool)):
			genome = pool[s]
			if genome[1] != None:
				continue
			winkeys.hit_key(keys_dict['space'], 0.05)
			score = test_individual(genome[0])
			pool[s] = (genome[0], score)
		pool = sorted(pool, key=lambda specie: specie[1], reverse=True)  	
		print pool
		
		if g % 2 == 0:
			write_species_to_file(g, pool)
		babies = []
		for i in range(4):
			for j in range(i+1,4):
				babies += get_nasty(pool[i][0], pool[j][0], current_genomes)
		pool+=babies
		print pool

	
def write_species_to_file(gen, pool):
	sorted(pool, key=lambda specie: specie[1], reverse=True)  
	with open('../data/gen'+str(gen), 'wb') as csvfile:
		 spamwriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		 for specie in pool[:min(250,len(pool))]:
		 	spamwriter.writerow([specie[0], specie[1]])

def populate_species_from_file(filename):
	pool = []
	with open(filename, 'rb') as csvfile:
		spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
		for row in spamreader:
			if len(row) < 2:
				pool.append((row[0], None))
			elif row[1] == "" or row[1] == None:
				pool.append((row[0], None))
			else:
				pool.append((row[0], float(row[1])))
	return pool

def get_nasty(genome0, genome1, already_seen, mutation_rate=0.02):
	pool = []
	quart = len(genome1)/4
	half = len(genome1)/2
	splice = "".join(i for j in zip(genome0, genome1) for i in j)
	if not splice[0:len(genome1)] in already_seen:
		pool.append((splice[0:len(genome1)], None))
	if not splice[len(genome1):] in already_seen:
		pool.append((splice[len(genome1):], None) )
	tempy = (genome0[0:quart]+genome1[quart:(2*quart)]+genome0[(2*quart):(3*quart)]+genome1[(3*quart):(4*quart)], None)
	if not tempy[0] in already_seen:
		pool.append(tempy)
	tempy = (genome1[0:quart]+genome0[quart:(2*quart)]+genome1[(2*quart):(3*quart)]+genome0[(3*quart):(4*quart)], None)
	if not tempy[0] in already_seen:
		pool.append(tempy)
	tempy = (genome0[0:half]+genome1[half:], None)
	if not tempy[0] in already_seen:
		pool.append(tempy)
	tempy = (genome1[0:half]+genome0[half:], None)
	if not tempy[0] in already_seen:
		pool.append(tempy)
	pool = add_mutations(pool, mutation_rate)
	return pool


def add_mutations(pool, rate):
	for g in range(len(pool)):
		genome = pool[g][0]
		new_genome = ""
		for i in range(len(genome)):
			muta = random.random()
			if muta <= rate:
				new_genome += muta_dict[random.randint(0,3)]
			else:
				new_genome += genome[i]
		pool[g] = (new_genome, None)
	return pool

if __name__ == '__main__':
  start_simulation()
  # get_score(True)