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
keys_dict = {'q':[0x10], 'w':[0x11], 'o':[0x18], 'p':[0x19], 'space':[0x39], 'r':[0x13],
						 'a':[0x10,0x11], 's':[0x10,0x18], 'd':[0x10,0x19], 'f':[0x11,0x18], 'g':[0x11,0x19], 'h':[0x19,0x18]}
muta_dict = {0:'p', 1:'p', 2:'w', 3:'q', 4:'s', 5:'d', 6:'f', 7:'g', 8:'a', 9:'h'}
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
		key = keys_dict[genome[c%n]]
		if len(key) > 1:
			winkeys.hit_key(key[0], 0.1, key[1])
		else:
			winkeys.hit_key(key[0], 0.1)
		c+=1
		if c > 300:
			score = get_score(True)
			print "stuck, resetting:"
			winkeys.hit_key(keys_dict['r'][0], 0.1)
			return score
	score = get_score()
	return score

def start_simulation(starting_file = None):
	worst_dude = (None, 0.0)
	base_str = "../data/gen"
	if starting_file == None:
		c = 0
		last_viable_gen = 0
		while os.path.isfile(base_str+str(c)):
			c+=1
		c-=1
		pool = populate_species_from_file(base_str+str(c))
	else:
		pool = populate_species_from_file(starting_file)
		c = int(starting_file[-1:])
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
			winkeys.hit_key(keys_dict['space'][0], 0.05)
			score = test_individual(genome[0])
			pool[s] = (genome[0], score)
			if score < worst_dude[1]:
				worst_dude = pool[s]
				print worst_dude
		pool = sorted(pool, key=lambda specie: specie[1], reverse=True)

		for victor in pool[0:10]:
			print victor[0][:20] + " " + str(victor[1])

		if g % 2 == 0:
			save_worst_dude(g, worst_dude)
			write_species_to_file(g, pool)
		babies = []
		for i in range(4):
			for j in range(i+1,4):
				babies += get_nasty(pool[i][0], pool[j][0], current_genomes)
		# rando couple
		babies += get_nasty(pool[random.randint(0,20)][0], pool[random.randint(0,20)][0], current_genomes)
		pool+=babies

def save_worst_dude(gen, worst_dude):
	with open('../data/worst_dude'+str(gen), 'wb') as csvfile:
		 spamwriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		 spamwriter.writerow([worst_dude[0], worst_dude[1]])

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

def get_nasty(genome0, genome1, already_seen, mutation_rate=0.05):
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
	for specie in pool:
		already_seen.add(specie[0])
	return pool


def add_mutations(pool, rate):
	for g in range(len(pool)):
		genome = pool[g][0]
		new_genome = ""
		for i in range(len(genome)):
			muta = random.random()
			if muta <= rate:
				new_genome += muta_dict[random.randint(0,7)]
			else:
				new_genome += genome[i]
		pool[g] = (new_genome, None)
	return pool

if __name__ == '__main__':
  start_simulation()
  # get_score(True)