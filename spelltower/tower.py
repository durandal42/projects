class Cell:
    value = '.'
    min_length = 0
    def __init__(self, value, min_length=0):
        self.value = value
        self.min_length = min_length
    def __str__(self):
        return value

class Tower:
    cells = {}
    width = 10

    def __init__(self, width=None, lines=None):
        self.cells = {}
        self.width = width
        if not lines: return
        for line in lines:
            self.append(line)

    def append(self, line):
        print 'adding tower row:',line
        for x,y in sorted(self.cells.keys()):
            self.cells[x-1,y] = self.at(x,y)
            del self.cells[x,y]
        y = 0
        for c in line.rstrip():
            if c.isdigit():
                y -= 1
                self.cells[13,y].min_length = int(c)
            elif c != ' ':
                self.cells[13,y] = Cell(c.upper())
            y += 1
            
    def occupied(self, x, y):
        return (x,y) in self.cells

    def at(self, x, y):
        if self.occupied(x,y):
            return self.cells[x,y]
        else:
            return None
        
    def copy(self):
        result = Tower()
        result.cells = self.cells.copy()
        result.width = self.width
        return result

    def __str__(self):
        return self.show()
    def show(self, play=None):
        touched = play and play.touched() or set()
        destroyed = self.find_destroyed(touched)
        result = '+' + ' - '*self.width + '+\n'
        for x in range(14):
            result += '|'
            for y in range(self.width):
                value = ' '
                frame = ' %s '
                if self.occupied(x,y):
                    cell = self.at(x,y)
                    value = cell.value
                if touched and (x,y) in touched:
                    frame = '[%s]'
                elif destroyed and (x,y) in destroyed:
                    frame = '>%s<'
                result += frame % value
            result += '|\n'
        result += '+' + ' - '*self.width + '+'
        return result

    def export(self):
        result = ''
        for x in range(14):
            line = ''
            for y in range(self.width):
                if self.occupied(x,y):
                    cell = self.at(x,y)
                    line += cell.value
                    if cell.min_length > 0:
                        line += str(cell.min_length)
                else:
                    line += ' '
            if line == ' '*self.width:
                continue
            result += line
            result += '\n'
        return result

    def update(self, play):
        for x,y in sorted(self.find_destroyed(play.touched())):
            self.destroy(x,y)
            
    def find_destroyed(self, touched):
        destroyed = touched.copy()
        for x,y in touched:
            for dx,dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                if (self.occupied(x+dx, y+dy) and
                    (len(touched) >= 5 or self.at(x+dx, y+dy).value == '.')):
                    destroyed.add((x+dx,y+dy))
        for x,y in touched:
            if self.at(x,y).value in ['Z', 'Q', 'J', 'X']:
                for y2 in range(self.width):
                    destroyed.add((x,y2))
        return destroyed

    def destroy(self, x,y):
        while x >= 0:
            if self.occupied(x,y):
                del self.cells[x,y]
            if self.occupied(x-1,y):
                self.cells[x,y] = self.at(x-1,y)
            x -= 1
