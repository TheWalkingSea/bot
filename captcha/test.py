
import math
class WaveDeformer():

    def transform(self, x, y):
        y = y + 12*math.sin(x/35)
        return x, y



    def transform_rectangle(self, x0, y0, x1, y1):
        return (*self.transform(x0, y0),
                *self.transform(x0, y1),
                *self.transform(x1, y1),
                *self.transform(x1, y0),
                )

    def getmesh(self, img):
        self.w, self.h = img.size
        gridspace = 20
        target_grid = []
        for x in range(0, self.w, gridspace):
            for y in range(0, self.h, gridspace):
                target_grid.append((x, y, 
                                    x + gridspace, y + gridspace))

        source_grid = [self.transform_rectangle(*rect)
                                 for rect in target_grid]

        return [t for t in zip(target_grid, source_grid)]

