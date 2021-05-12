
import numpy as np
import ipywidgets as widgets
from ipywidgets import Layout
import re
import Data
import gurobipy as gp
from gurobipy import GRB
from scipy.spatial import ConvexHull

def prevals():
    springs = []
    constraints = []
    flag = np.array([1, 0, 0, 0, 1, 0, 0, 0, 0, 0])
    props = np.array([[0, 29500, 29500, 0.3, 0.3, 29500 / (2 * (1 + 0.3))]])
    nodes =np.array([[1, 1, 3], [2, 1, 5],
                [3, 1, 3], [4, 1, 1],
                [4, 1, 2], [5, 2, 3]])
    elements = np.array([[0, 0, 1, 0.059, 0], [1, 1, 2, 0.059, 0], [2, 2, 3, 0.059, 0],
                    [3, 3, 4, 0.059, 0], [4, 4, 5, 0.059, 0], [5, 5, 6, 0.059, 0],
                    [6, 6, 7, 0.059, 0], [7, 7, 8, 0.059, 0], [8, 8, 9, 0.059, 0]])
    return props, nodes, elements, springs, constraints, flag
class MainPrePro:
    def optimize(self):
        ien = Data.DATA['ien']
        xn = Data.DATA['xn']
        idb = Data.DATA['idb']
        m = gp.Model('mip')
        C = []
        S = []
        D = []
        num = 0
        for i in range(len(xn.T)):
            C.append(m.addVar(vtype = GRB.INTEGER, name = 'C'+str(i)))
            S.append(m.addVar(vtype = GRB.INTEGER, name = 'S'+str(i)))
            D.append(m.addVar(vtype = GRB.INTEGER, name = 'D'+str(i)))
            num+=int(xn[1, i])
        m.setObjective(-sum(C), GRB.MAXIMIZE)
        for i in range(1, len(idb)):
            if i!=0:
                for j in range(len(idb[i])):
                    m.addConstr(S[i]>=S[int(idb[i][j])-1]+D[int(idb[i][j])-1])
        m.addConstr(78>=S[6]+D[6])
        num = 0
        for i in range(len(xn.T)):
            m.addConstr(S[i]>=0)
            m.addConstr(D[i]>=min(ien[2][num:num+int(xn[1, i])]))
            m.addConstr(D[i]<=max(ien[2][num:num+int(xn[1, i])]))
            m.addConstr(C[i]>=min(ien[3][num:num+int(xn[1, i])]))
            m.addConstr(C[i]<=max(ien[3][num:num+int(xn[1, i])]))
            num+=int(xn[1, i])
        num = 0
        count = 0
        for i in range(len(xn.T)):
            points = np.zeros((int(xn[1, i])+1, 2))
            points[0, :] = [10000000, 10000000]
            points[1:, 0] = ien[2][num:num+int(xn[1, i])]
            points[1:, 1] = ien[3][num:num+int(xn[1, i])]
            hull = ConvexHull(points)
            for j in range(1, len(hull.vertices)-1):
                Mij = (points[hull.vertices[j+1],1]-points[hull.vertices[j],1])/(points[hull.vertices[j+1],0]-points[hull.vertices[j],0])
                Bij = points[hull.vertices[j+1],1] - Mij*points[hull.vertices[j+1],0]
                m.addConstr(C[i] >= Mij*D[i]+Bij)
            num+=int(xn[1, i])
        m.update()
        m.optimize()
        out = np.zeros((len(xn.T), 4))
        out[:, 0] = [i+1 for i in range(len(xn.T))]
        for enum, v in enumerate(m.getVars()):
            out[int(enum/3), enum%3+1] = v.x
        self.outTitle = widgets.Label(value='Schedule')
        self.outtext = ['Task#','Start', 'Duration', 'End', 'Cost']
        self.outs = [[] for i in range(len(out))]
        self.oitems = [[] for i in range(len(out))]
        self.olabel= widgets.HBox([widgets.Label(value=self.outtext[j], layout = widgets.Layout(width='120px')) for j in range(len(self.outtext))])
        for i in range(len(out)):
            if(i<len(out)):
                self.oitems[i].append(widgets.FloatText(value=out[i][0], layout = widgets.Layout(width='120px', height = '22px')))
                self.oitems[i].append(widgets.FloatText(value=out[i][2], layout = widgets.Layout(width='120px', height = '22px')))
                self.oitems[i].append(widgets.FloatText(value=out[i][3], layout = widgets.Layout(width='120px', height = '22px')))
                self.oitems[i].append(widgets.FloatText(value=out[i][2]+out[i][3], layout = widgets.Layout(width='120px', height = '22px')))
                self.oitems[i].append(widgets.FloatText(value=out[i][1], layout = widgets.Layout(width='120px', height = '22px')))
                self.outs[i] = widgets.HBox(self.oitems[i], layout=widgets.Layout(width = '800px', height = '30px'))
        Dl = widgets.Label(value=  'Total Duration', layout = widgets.Layout(width='120px'))
        D = widgets.FloatText(value=np.max(out[:, 2]+out[:, 3]), layout = widgets.Layout(width='120px', height = '22px'))
        Tl = h = widgets.Label(value=  'Total Cost', layout = widgets.Layout(width='120px'))
        T = widgets.FloatText(value=-m.objVal, layout = widgets.Layout(width='120px', height = '22px'))
        self.outf = widgets.HBox([Dl, D, Tl, T])
        self.outr0 = widgets.VBox([self.outs[j] for j in range(len(out))])
        self.onode = widgets.VBox([self.outTitle, self.olabel, self.outr0, self.outf], layout= widgets.Layout(border = 'solid 1px black'))
        display(self.onode)

    def getNumbers(self, str): 
        array = re.findall(r'[0-9]+', str) 
        return array
    def add_node(self, b):
        New_row = widgets.HBox(self.nitems[len(self.nitems)-1], layout=widgets.Layout(width = '490px', height = '30px'))
        self.noder0.children = self.noder0.children + (New_row,)
    def del_node(self, b):
        del_row = list(self.noder0.children)
        del_row = del_row[:-1]
        self.noder0.children = tuple(del_row)
    def nodes_widget(self, nodes):
        self.nodTitle = widgets.Label(value='Nodes')
        self.nodetext = ['Task#','Precedence', 'Options']
        self.nodes = nodes
        self.node = [[] for i in range(len(self.nodes))]
        self.nitems = [[] for i in range(len(self.nodes))]
        ADDNODE = widgets.Button(description="Add Node", layout= widgets.Layout(width='120px', border = 'solid 1px black'))
        DELNODE = widgets.Button(description="Remove Node", layout= widgets.Layout(width='120px', border = 'solid 1px black'))
        self.Submit = widgets.Button(description = 'Submit', layout= widgets.Layout(width='120px', border = 'solid 1px black'))
        self.nlabel= widgets.HBox([widgets.Label(value=self.nodetext[j], layout = widgets.Layout(width='120px')) for j in range(len(self.nodetext))])
        for i in range(len(self.nodes)):
            if(i<len(self.nodes)):
                for j in range(3):
                    if j!= 1:
                        self.nitems[i].append(widgets.FloatText(value=self.nodes[i][j], layout = widgets.Layout(width='120px', height = '22px')))
                    if j == 1:
                        self.nitems[i].append(widgets.Text(value=str(self.nodes[i][j]), layout = widgets.Layout(width='120px', height = '22px')))
                self.node[i] = widgets.HBox(self.nitems[i], layout=widgets.Layout(width = '600px', height = '30px'))
        self.noder0 = widgets.VBox([self.node[j] for j in range(len(self.nodes))])
        self.brow = widgets.HBox([ADDNODE, DELNODE, self.Submit])
        self.rnode = widgets.VBox([self.nodTitle, self.nlabel, self.noder0, self.brow], layout= widgets.Layout(border = 'solid 1px black'))
        ADDNODE.on_click(self.add_node)
        DELNODE.on_click(self.del_node)
        self.Submit.on_click(self.fsubmit)
        self.rnode

        return self.rnode, ADDNODE
        # return nodTitle, nlabel, noder0, brow

    def fsubmit(self, b):
        self.xn = np.zeros((2, len(self.noder0.children)))
        self.idb = [[] for i in range(len(self.noder0.children))]
        # self.f = np.zeros((self.dims, len(self.noder0.children)))
        # self.g = np.zeros((self.dims, len(self.noder0.children)))
        for j in range(len(self.noder0.children)):
            self.xn[0, j] = self.noder0.children[j].children[0].value
            self.xn[1, j] = self.noder0.children[j].children[2].value
            strg = self.noder0.children[j].children[1].value
            self.idb[j] =self.getNumbers(strg)
            # self.f[i, j] = self.noder0.children[j].children[i+1+2*self.dims].value
            # self.g[i, j] = self.noder0.children[j].children[i+1+3*self.dims].value
        # self.ien = np.zeros((2, len(self.ien1r0.children)))
        # self.A = np.zeros(len(self.ien1r0.children))
        # self.E = np.zeros(len(self.ien1r0.children))
        # for j in range(len(self.ien1r0.children)):
        #     for i in range(2):
        #         self.ien[i, j] = self.ien1r0.children[j].children[i+1].value
        #     self.E[j] = self.ien1r0.children[j].children[3].value
        #     self.A[j] = self.ien1r0.children[j].children[4].value
        # self.nsd = self.dims
        # self.ndf = self.minp[1]
        # self.nen = self.minp[2]

        Data.DATA['xn'] = self.xn
        Data.DATA['idb'] = self.idb
        self.wprops(self.xn, self.idb, self.options)
        # Data.DATA['ien'] = self.ien
        # Data.DATA['E'] = self.E
        # Data.DATA['A'] = self.A
        # Data.DATA['f'] = self.f
        # Data.DATA['g'] = self.g
        # Data.DATA['nsd'] = self.nsd
        # Data.DATA['ndf'] = self.ndf
        # Data.DATA['nen'] = self.nen
        # Data.DATA['nel'] = len(self.ien1r0.children)
        # Data.DATA['nnp'] = len(self.noder0.children)

    def add_material(self, b):
        self.ien = np.zeros((4, len(self.matr.children)))
        for j in range(len(self.matr.children)):
            for i in range(4):
                self.ien[i, j] = self.matr.children[j].children[i].value
        Data.DATA['ien'] = self.ien
        self.optimize()

    def del_material(self, b):
        del_row = list(self.matr.children)
        del_row = del_row[:-1]
        self.noder0.children = tuple(del_row)

    def wprops(self, xn, idb, props):
        matTitle = widgets.Label(value='Activity Options List')
        mattext = ['Task#', 'Option#', 'Duration', 'Cost']
        self.props = props
        prop = [[] for i in range(int(np.sum(xn[1, :])))]
        self.mitems = [[] for i in range(int(np.sum(xn[1, :])))]
        self.ADDMAT = widgets.Button(description="Submit", layout= widgets.Layout(border = 'solid 1px black'))
        # self.DELMAT = widgets.Button(description="Remove Material", layout= widgets.Layout(border = 'solid 1px black'))
        # matlabel = widgets.GridBox([widgets.Label(value=mattext[j]) for j in range(len(mattext))], layout=widgets.Layout(grid_template_columns="repeat(6, 50px[col-start])"))
        matlabel= widgets.HBox([widgets.Label(value=mattext[j], layout = widgets.Layout(width='120px')) for j in range(len(mattext))])
        num = -1
        val = True if len(self.props)==24 else False
        for i in range(int(len(xn.T))):
            for z in range(int(xn[1, i])):
                num+=1
                if val:
                    for j in range(len(mattext)):
                        self.mitems[num].append(widgets.FloatText(value=self.props[num,j], layout = widgets.Layout(width='120px')))
                else:
                    self.mitems[num].append(widgets.FloatText(value = i), layout = widgets.Layout(width='120px'))
                    self.mitems[num].append(widgets.FloatText(value = z), layout = widgets.Layout(width='120px'))
                    self.mitems[nun].append(widgets.FloatText(value = 0), layout = widgets.Layout(width='120px'))
                    self.mitems[nun].append(widgets.FloatText(value = 0), layout = widgets.Layout(width='120px'))
                prop[num] = widgets.HBox(self.mitems[num], layout=widgets.Layout(width = '800px', height = '30px'))
                    # prop[i] = widgets.GridBox(self.mitems[i], layout=widgets.Layout(grid_template_columns="repeat(6, 50px[col-start])"))
        self.matr = widgets.VBox([prop[j] for j in range(len(prop))])
        # brow = widgets.HBox([self.ADDMAT, self.DELMAT])
        self.rowm = widgets.VBox([matTitle, matlabel, self.matr, self.ADDMAT], layout= widgets.Layout(border = 'solid 1px black'))
        self.ADDMAT.on_click(self.add_material)
        # self.DELMAT.on_click(self.del_material)
        display(self.rowm)
        return self.rowm, self.ADDMAT

    def run(self):
        # self.nodes = nodes
        # self.props = props
        m=1
        self.m = m
        nodes =[[1, '1', 3], [2, '1', 5],
                [3, '1', 3], [4, '1', 3],
                [5, '2, 3', 4], [6, '4', 3], [7, '5, 6', 3]]
        options = np.array([[1, 1, 14, 23000], [1, 2, 20, 18000], [1, 3, 24, 12000], 
                            [2, 1, 15, 3000], [2, 2, 18, 2400], [2, 3, 20, 1800],[2, 4, 23, 1500], [2, 5, 25, 1000],
                            [3, 1, 15, 4500],[3, 2, 22, 4000], [3, 3, 33, 3200],
                            [4, 1, 12, 45000],[4, 2, 16, 35000], [4, 3, 20, 30000],
                            [5, 1, 22, 22000],[5, 2, 24, 17500], [5, 3, 28, 15000], [5, 4, 30, 10000],
                            [6, 1, 14, 40000], [6, 2, 18, 32000], [6, 3, 24, 18000],
                            [7, 1, 9, 30000], [7, 2, 15, 24000], [7, 3, 18, 22000]])
        self.nodes = nodes
        self.options = options
        self.rnode, ADDNODE = self.nodes_widget(self.nodes)
        # self.rowm, self.ADDMAT, self.DELMAT = self.wprops(self.props, self.m)
        # self.page = widgets.VBox([self.rowm, self.rnode])

        return self.rnode
