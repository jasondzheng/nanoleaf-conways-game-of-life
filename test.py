import unittest
from conwaysgameoflife import ConwaysGameOfLife

class TestConwaysGameOfLife(unittest.TestCase):
    def setUp(self):
        self.game = ConwaysGameOfLife(5, 5)

    def test_block(self):
        self.game.batch_set([
            (0, 0), (1, 0),
            (0, 1), (1, 1)
        ])
        old_state = set(self.game.dump_state())
        self.game.tick()
        new_state = set(self.game.dump_state())
        self.assertEqual(new_state, old_state)

    def test_beehive(self):
        self.game.batch_set([
                    (1, 0), (2, 0),
            (0, 1),                 (3, 1),
                    (1, 2), (2, 2)
        ])
        old_state = set(self.game.dump_state())
        self.game.tick()
        new_state = set(self.game.dump_state())
        self.assertEqual(new_state, old_state)

    def test_blinker(self):
        self.game.batch_set([
                    (1, 0),
                    (1, 1),
                    (1, 2)
        ])
        old_state = set(self.game.dump_state())
        self.game.tick()
        new_state = set(self.game.dump_state())
        self.assertEqual(new_state.difference(old_state), {
                    (1, 0, False),
            (0, 1, True),         (2, 1, True),
                    (1, 2, False)
        })

if __name__ == '__main__':
    unittest.main()