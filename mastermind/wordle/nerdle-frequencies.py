import collections

zzd = collections.Counter()
z1d = collections.Counter()
z2d = collections.Counter()
for x1 in range(10):
    for x2 in range(10):
        for y1 in range(10):
            for y2 in range(10):
                zz = x1*10 + x2 + y1*10 + y2
                if zz > 99: continue
                if zz < 10: continue
                if zz != int(zz): continue
                zzd[zz] += 1
                z2, z1 = zz % 10, int(zz / 10)
                z1d[z1] += 1
                z2d[z2] += 1

print("zz:")
for k,v in zzd.items():
    print(k,v)
print("z1:")
for k,v in z1d.items():
    print(k,v)
print("z2:")
for k,v in z2d.items():
    print(k,v)

