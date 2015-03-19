import unittest
from tempfile import NamedTemporaryFile

from bitcoingraph.graph import *
from bitcoingraph.blockchain import BlockChain

from tests.rpc_mock import BitcoinProxyMock


LOG = True
LOGFILE = "/tmp/test_graph.log"
LOGLVL = "DEBUG"

TEST_CSV = 'tests/data/tx_graph.csv'

class TestGraph(unittest.TestCase):

    def setUp(self):
        self.graph = Graph(customlogger=self._logger)

    @classmethod
    def setUpClass(cls):
        """ 
        config logging if available and initialize edges 
        """
        if LOG:
            formatter = logging.Formatter( '%(levelname)s \t- %(message)s' )
            numeric_level = getattr(logging, LOGLVL , None)
            cls._logger = logging.getLogger("test")
            cls._logger.setLevel(level=numeric_level)

            cls._logfile = logging.FileHandler( LOGFILE,mode='a',encoding=None,delay=False)
            cls._logfile.setLevel( numeric_level )
            cls._logfile.setFormatter( formatter )
            cls._logger.addHandler( cls._logfile )

    @classmethod
    def tearDownClass(cls):
        """
        close logger if available and delete edges
        """
        if LOG:
            cls._logfile.close()
            logging.shutdown()
            del cls._logfile
            del cls._logger


    def test_add_edge(self):
        
        edge1 = { SRC: 'A', DST: 'B' }
        self.graph.add_edge(edge1)
        self.assertEqual(1, self.graph.count_edges())

        i = 0
        for edge in self.graph.list_edges():
            self.assertTrue(edge[EDGE] == 1)
            self.assertTrue(edge[SRC] == "A")
            self.assertTrue(edge[DST] == "B")
            i += 1
        self.assertTrue(i == 1)

        edge2 = { DST: 'C', EDGE: '2' }
        self.assertRaises(GraphException, self.graph.add_edge, edge2)

        edge3 = { SRC: 'A', EDGE: '3' }
        self.assertRaises(GraphException, self.graph.add_edge, edge3)


    def test_count_edges(self):
        edge1 = {SRC: 'A', DST: 'B', EDGE: '1'}
        self.graph.add_edge(edge1)
        self.assertEqual(1, self.graph.count_edges())
        edge2 = {SRC: 'A', DST: 'C', EDGE: '2'}
        self.graph.add_edge(edge2)
        self.assertEqual(2, self.graph.count_edges())

    def test_list_edges(self):
        edge1 = {SRC: 'A', DST: 'B', EDGE: '1'}
        self.graph.add_edge(edge1)
        edge2 = {SRC: 'A', DST: 'C', EDGE: '2'}
        self.graph.add_edge(edge2)
        edge3 = {SRC: 'A', DST: 'E', EDGE: '3'}
        self.graph.add_edge(edge3)
        edges = [edge for edge in self.graph.list_edges()]
        self.assertIn(edge1, edges)
        self.assertIn(edge2, edges)
        self.assertIn(edge3, edges)

    def test_find_edges(self):
        self.assertEqual(0, self.graph.count_edges())

        edge13 = {SRC: 'E', DST: 'A', EDGE: '13'}
        self.graph.add_edge(edge13)
        edge2 = {SRC: 'A', DST: 'B', EDGE: '2'}
        self.graph.add_edge(edge2)
        edge3 = {SRC: 'A', DST: 'E', EDGE: '3'}
        self.graph.add_edge(edge3)
        edge4 = {SRC: 'B', DST: 'D', EDGE: '4'}
        self.graph.add_edge(edge4)

        edges = self.graph.find_edges("A")
        self.assertIn(edge13, edges)
        self.assertIn(edge2, edges)
        self.assertIn(edge3, edges)
        self.assertNotIn(edge4, edges)

    def test_find_edges_unknown_key(self):
        edge = {SRC: 'E', DST: 'A', EDGE: '13'}
        self.graph.add_edge(edge)
        edges = self.graph.find_edges('C')
        self.assertFalse(edges)

    def test_find_edge(self):
        self.assertEqual(0, self.graph.count_edges())

        edge1 = {SRC: 'E', DST: 'A', EDGE: '13', TIMESTAMP: 444}
        self.graph.add_edge(edge1)
        edge2 = {SRC: 'A', DST: 'C', EDGE: '2', TIMESTAMP: 333}
        self.graph.add_edge(edge2)
        edge3 = {SRC: 'A', DST: 'E', EDGE: '3', TIMESTAMP: 222}
        self.graph.add_edge(edge3)
        edge4 = {SRC: 'A', DST: 'B', EDGE: '1', TIMESTAMP: 111}
        self.graph.add_edge(edge4)

        edge = self.graph.find_edge("A")
        self.assertIn(edge4, [ edge ])
        self.assertNotIn(edge1, [ edge ])
        self.assertNotIn(edge2, [ edge ])
        self.assertNotIn(edge3, [ edge ])


    def test_find_edges_xy(self):
        self.assertEqual(0, self.graph.count_edges())

        edge1 = {SRC: 'A', DST: 'B', EDGE: '1'}
        edge2 = {SRC: 'A', DST: 'C', EDGE: '2'}
        edge3 = {SRC: 'A', DST: 'E', EDGE: '3'}
        self.graph.add_edge(edge1)
        self.graph.add_edge(edge2)
        self.graph.add_edge(edge3)

        edge4 = {SRC: 'B', DST: 'D', EDGE: '4'}
        edge5 = {SRC: 'B', DST: 'F', EDGE: '5'}
        self.graph.add_edge(edge4)
        self.graph.add_edge(edge5)

        edge6 = {SRC: 'C', DST: 'G', EDGE: '6'}
        self.graph.add_edge(edge6)

        edge13 = {SRC: 'E', DST: 'A', EDGE: '13'}
        self.graph.add_edge(edge13)

        edge7 = {SRC: 'D', DST: 'H', EDGE: '7'}
        edge8 = {SRC: 'D', DST: 'I', EDGE: '8'}
        self.graph.add_edge(edge7)
        self.graph.add_edge(edge8)

        edge9 = {SRC: 'F', DST: 'E', EDGE: '9'}
        self.graph.add_edge(edge9)

        edge10 = {SRC: 'G', DST: 'F', EDGE: '10'}
        self.graph.add_edge(edge10)

        edge11 = {SRC: 'I', DST: 'H', EDGE: '11'}
        edge12 = {SRC: 'I', DST: 'F', EDGE: '12'}
        edge14 = {SRC: 'I', DST: 'F', EDGE: '14'}
        self.graph.add_edge(edge11)
        self.graph.add_edge(edge12)
        self.graph.add_edge(edge14)

        edges = self.graph.find_edges_xy("I","F")
        self.assertIn(edge12, edges)
        self.assertIn(edge14, edges)

        self.assertNotIn(edge13, edges)
        self.assertNotIn(edge11, edges)
        self.assertNotIn(edge10, edges)
        self.assertNotIn(edge9, edges)
        self.assertNotIn(edge8, edges)
        self.assertNotIn(edge7, edges)
        self.assertNotIn(edge6, edges)
        self.assertNotIn(edge5, edges)
        self.assertNotIn(edge4, edges)
        self.assertNotIn(edge3, edges)
        self.assertNotIn(edge2, edges)
        self.assertNotIn(edge1, edges)

    def test_find_edge_x2y(self):
        self.assertEqual(0, self.graph.count_edges())

        edge1 = {SRC: 'A', DST: 'B', EDGE: '1'}
        edge2 = {SRC: 'A', DST: 'C', EDGE: '2'}
        edge3 = {SRC: 'A', DST: 'E', EDGE: '3'}
        self.graph.add_edge(edge1)
        self.graph.add_edge(edge2)
        self.graph.add_edge(edge3)

        edge4 = {SRC: 'B', DST: 'D', EDGE: '4'}
        edge5 = {SRC: 'B', DST: 'F', EDGE: '5'}
        self.graph.add_edge(edge4)
        self.graph.add_edge(edge5)

        edge6 = {SRC: 'C', DST: 'G', EDGE: '6'}
        self.graph.add_edge(edge6)

        edge13 = {SRC: 'E', DST: 'A', EDGE: '13'}
        self.graph.add_edge(edge13)

        edge7 = {SRC: 'D', DST: 'H', EDGE: '7'}
        edge8 = {SRC: 'D', DST: 'I', EDGE: '8'}
        self.graph.add_edge(edge7)
        self.graph.add_edge(edge8)

        edge9 = {SRC: 'F', DST: 'E', EDGE: '9'}
        self.graph.add_edge(edge9)

        edge10 = {SRC: 'G', DST: 'F', EDGE: '10'}
        self.graph.add_edge(edge10)

        edge11 = {SRC: 'I', DST: 'H', EDGE: '11'}
        edge12 = {SRC: 'I', DST: 'F', EDGE: '12'}
        edge14 = {SRC: 'I', DST: 'F', EDGE: '14'}
        self.graph.add_edge(edge11)
        self.graph.add_edge(edge12)
        self.graph.add_edge(edge14)

        edges = self.graph.find_edge_x2y("A","F",2)
        self.assertIn(edge1, edges)
        self.assertIn(edge5, edges)

        self.assertNotIn(edge14, edges)
        self.assertNotIn(edge13, edges)
        self.assertNotIn(edge12, edges)
        self.assertNotIn(edge11, edges)
        self.assertNotIn(edge10, edges)
        self.assertNotIn(edge9, edges)
        self.assertNotIn(edge8, edges)
        self.assertNotIn(edge7, edges)
        self.assertNotIn(edge6, edges)
        self.assertNotIn(edge4, edges)
        self.assertNotIn(edge3, edges)
        self.assertNotIn(edge2, edges)

    def test_find_edges_x2y_selfreference(self):
        self.assertEqual(0, self.graph.count_edges())

        edge1 = {SRC: 'A', DST: 'B', EDGE: '1'}
        edge2 = {SRC: 'A', DST: 'C', EDGE: '2'}
        edge3 = {SRC: 'A', DST: 'E', EDGE: '3'}
        self.graph.add_edge(edge1)
        self.graph.add_edge(edge2)
        self.graph.add_edge(edge3)

        edge4 = {SRC: 'B', DST: 'D', EDGE: '4'}
        edge5 = {SRC: 'B', DST: 'F', EDGE: '5'}
        self.graph.add_edge(edge4)
        self.graph.add_edge(edge5)

        edge6 = {SRC: 'C', DST: 'G', EDGE: '6'}
        self.graph.add_edge(edge6)

        edge13 = {SRC: 'E', DST: 'A', EDGE: '13'}
        self.graph.add_edge(edge13)

        edge7 = {SRC: 'D', DST: 'H', EDGE: '7'}
        edge8 = {SRC: 'D', DST: 'I', EDGE: '8'}
        self.graph.add_edge(edge7)
        self.graph.add_edge(edge8)

        edge9 = {SRC: 'F', DST: 'E', EDGE: '9'}
        self.graph.add_edge(edge9)

        edge10 = {SRC: 'G', DST: 'F', EDGE: '10'}
        self.graph.add_edge(edge10)

        edge11 = {SRC: 'I', DST: 'H', EDGE: '11'}
        edge12 = {SRC: 'I', DST: 'F', EDGE: '12'}
        edge14 = {SRC: 'I', DST: 'F', EDGE: '14'}
        self.graph.add_edge(edge11)
        self.graph.add_edge(edge12)
        self.graph.add_edge(edge14)

        edge88 = {SRC: 'A', DST: 'A', EDGE: '88'}
        self.graph.add_edge(edge88)
        
        edge888 = {SRC: 'B', DST: 'B', EDGE: '888'}
        self.graph.add_edge(edge888)

        edgeslist = self.graph.find_edges_x2y("A","F",4)
        n = 0
        for edges in edgeslist:
            self._logger.debug("Path {} of {}".format(n,len(edgeslist)))
            n += 1
            for edge in edges:
                self._logger.debug("\t{}".format(edge))
        self.assertTrue(len(edgeslist) == 4, "Invalid number of Paths")

        #invalid contition
        #self.assertIn(edge7, edgeslist)

        for edges in edgeslist:
            for edge in edges:
                if edge[SRC] == "G":
                    self.assertIn(edge2, edges)
                    self.assertIn(edge6, edges)
                    self.assertIn(edge10, edges)

                    self.assertNotIn(edge1, edges)
                    self.assertNotIn(edge3, edges)
                    self.assertNotIn(edge4, edges)
                    self.assertNotIn(edge5, edges)
                    self.assertNotIn(edge7, edges)
                    self.assertNotIn(edge8, edges)
                    self.assertNotIn(edge9, edges)
                    self.assertNotIn(edge11, edges)
                    self.assertNotIn(edge12, edges)
                    self.assertNotIn(edge13, edges)
                    self.assertNotIn(edge14, edges)

                if edge[SRC] == "I":
                    self.assertIn(edge1, edges)
                    self.assertIn(edge4, edges)
                    self.assertIn(edge8, edges)

                    #self.assertIn(edge12, edges)
                    #self.assertIn(edge14, edges)

                    self.assertNotIn(edge2, edges)
                    self.assertNotIn(edge3, edges)
                    self.assertNotIn(edge5, edges)
                    self.assertNotIn(edge6, edges)
                    self.assertNotIn(edge7, edges)
                    self.assertNotIn(edge9, edges)
                    self.assertNotIn(edge10, edges)
                    self.assertNotIn(edge11, edges)
                    self.assertNotIn(edge13, edges)

                if edge[SRC] == "E":
                    self.assertIn(edge3, edges)
                    self.assertIn(edge13, edges)
                    self.assertIn(edge1, edges)
                    self.assertIn(edge5, edges)

                    self.assertNotIn(edge2, edges)
                    self.assertNotIn(edge4, edges)
                    self.assertNotIn(edge6, edges)
                    self.assertNotIn(edge7, edges)
                    self.assertNotIn(edge8, edges)
                    self.assertNotIn(edge9, edges)
                    self.assertNotIn(edge10, edges)
                    self.assertNotIn(edge11, edges)
                    self.assertNotIn(edge12, edges)
                    self.assertNotIn(edge14, edges)


            self.assertNotIn(edge7, edges)


