import os
import sys
import unittest
import torch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import _calc_feat_flatten_mean_std, adaptive_instance_normalization, calc_mean_std, _mat_sqrt, coral


class TestUtilsFunctions(unittest.TestCase):
    def test_calc_mean_std(self):
        inp = torch.ones(1, 16, 32, 32)
        eps = 1e-5
        res_mean, res_std = calc_mean_std(inp, eps=eps)

        self.assertEqual(res_mean.shape[1], 16)
        self.assertEqual(res_std.shape[1], 16)
        self.assertAlmostEqual(res_mean[0][0][0][0].item(), 1.0)
        self.assertAlmostEqual(res_std[0][0][0][0].item(), eps ** 0.5)

    def test_adaptive_instance_normalization(self):
        eps = 1e-5
        res = adaptive_instance_normalization(torch.randn(1, 16, 32, 32), torch.ones(1, 16, 32, 32))
        self.assertAlmostEqual(res[0][0].mean().item(), 1.0, places=2)
        self.assertAlmostEqual(res[0][0].std().item(), eps ** 0.5, places=2)

    def test__calc_feat_flatten_mean_std(self):
        inp = torch.ones(1, 3, 32, 32)
        res_flat, res_mean, res_std = _calc_feat_flatten_mean_std(inp)

        self.assertEqual(res_flat.shape[1], 32 * 32)
        self.assertAlmostEqual(res_mean[0][0].item(), 1.0)
        self.assertAlmostEqual(res_std[0][0].item(), 0.0)

    def test_mat_sqrt(self):
        inp = torch.eye(32, 32) * 2
        res = _mat_sqrt(inp)
        self.assertAlmostEqual(res[0][0].item(), 2 ** 0.5)

    def test_coral(self):
        img1 = torch.ones((1, 3, 32, 32)) * 2
        img1[:, :, 16:] = 0
        img2 = torch.ones((1, 3, 32, 32))
        img2[:, :, 16:] = 3.0
        res = coral(img1, img2)
        self.assertAlmostEqual(res[0][0][0][0].item(), 3.0, places=2)
        self.assertAlmostEqual(res[0][0][-1][-1].item(), 1.0, places=2)


if __name__ == "__main__":
    unittest.main()