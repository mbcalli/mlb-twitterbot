import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

inning_states = ['top','top','top','top','top','top','top','top','top','bottom','bottom','bottom','bottom','bottom','bottom','bottom','bottom','bottom','bottom','bottom','top','top','top','top','top','top','top','top','top','bottom','bottom','bottom','bottom','bottom','bottom']
xs = list(range(0, 50))
ys = list(range(0, 50))
print(xs)
bottom_indicies = [i for i, x in enumerate(inning_states) if x == 'bottom']

bottom_boundaries = []

for i in range(len(bottom_indicies)):
	if i == 0:
		bottom_boundaries.append(bottom_indicies[i])
	elif bottom_indicies[i] - bottom_indicies[i-1] > 1:
		bottom_boundaries.append(bottom_indicies[i-1])
		bottom_boundaries.append(bottom_indicies[i])
	elif i == len(bottom_indicies)-1:
		bottom_boundaries.append(bottom_indicies[i])


print(bottom_boundaries)

fig = plt.figure()
plt.rcParams.update({'font.size': 24})
plt.plot(xs, ys)
for i in range(0, len(bottom_boundaries), 2):
	plt.axvspan(bottom_boundaries[i], bottom_boundaries[i+1], color=(0.9, 0.9, 0.9, 0.8))
	plt.axvline(bottom_boundaries[i+1], color='k', linewidth=3.0)
fig.set_size_inches(24, 14)
plt.savefig('/home/pi/twitterbot/' + 'test' + '.png', dpi=100)
