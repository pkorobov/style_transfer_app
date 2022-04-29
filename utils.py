import torch


def calc_mean_std(feat, eps=1e-5):
    """Calculates channel-wise means and stds.

    Args:
        feat (torch.Tensor): The tensor to get means and stds from.
        eps (float): A small value added to the variance to avoid divide-by-zero

    Returns:
       A tuple of two torch.Tensor items.
       The first is channel-wise mean values. The second is channel-wise std values.
    """
    size = feat.size()
    assert len(size) == 4
    N, C = size[:2]
    feat_var = feat.view(N, C, -1).var(dim=2) + eps
    feat_std = feat_var.sqrt().view(N, C, 1, 1)
    feat_mean = feat.view(N, C, -1).mean(dim=2).view(N, C, 1, 1)
    return feat_mean, feat_std


def adaptive_instance_normalization(content_feat, style_feat):
    """Changes content_feat means and stds to style_feat ones.

    Args:
        content_feat (torch.Tensor): The tensor to get means and stds from.
        style_feat (torch.Tensor): A small value added to the variance to avoid divide-by-zero

    Returns:
       torch.Tensor.
       A tensor with shifted means and stds to style ones.
    """
    assert content_feat.size()[:2] == style_feat.size()[:2]
    size = content_feat.size()
    style_mean, style_std = calc_mean_std(style_feat)
    content_mean, content_std = calc_mean_std(content_feat)

    normalized_feat = (content_feat - content_mean.expand(size)) / content_std.expand(size)
    return normalized_feat * style_std.expand(size) + style_mean.expand(size)


def _calc_feat_flatten_mean_std(feat):
    """Gets means and stds of flattened image tensor.

    Args:
        feat (torch.Tensor): The tensor to get means and stds from.

    Returns:
       tuple of three torch.Tensor items.
       A flattened tensor, its means, stds.
    """
    feat_flatten = feat.view(3, -1)
    mean = feat_flatten.mean(dim=-1, keepdim=True)
    std = feat_flatten.std(dim=-1, keepdim=True)
    return feat_flatten, mean, std


def _mat_sqrt(x):
    """Transforms x matrix to its square root.

    Args:
        feat (torch.Tensor): The tensor to get square root from.

    Returns:
       torch.Tensor.
       A matrix root.
    """
    U, D, V = torch.svd(x)
    return torch.mm(torch.mm(U, D.pow(0.5).diag()), V.t())


def coral(source, target):
    """Changes source colors to target ones.
    Args:
        source (torch.Tensor): The image tensor to transform colors.
        target (torch.Tensor): The image tensor to get colors from.
    Returns:
       torch.Tensor.
       Source image tensor with transformed colors.
    """
    source_f, source_f_mean, source_f_std = _calc_feat_flatten_mean_std(source)
    source_f_norm = (source_f - source_f_mean.expand_as(source_f)) / source_f_std.expand_as(
        source_f
    )
    source_f_cov_eye = torch.mm(source_f_norm, source_f_norm.t()) + torch.eye(3)

    target_f, target_f_mean, target_f_std = _calc_feat_flatten_mean_std(target)
    target_f_norm = (target_f - target_f_mean.expand_as(target_f)) / target_f_std.expand_as(
        target_f
    )
    target_f_cov_eye = torch.mm(target_f_norm, target_f_norm.t()) + torch.eye(3)

    source_f_norm_transfer = torch.mm(
        _mat_sqrt(target_f_cov_eye),
        torch.mm(torch.inverse(_mat_sqrt(source_f_cov_eye)), source_f_norm),
    )

    source_f_transfer = source_f_norm_transfer * target_f_std.expand_as(
        source_f_norm
    ) + target_f_mean.expand_as(source_f_norm)

    return source_f_transfer.view(source.size())


def style_transfer(vgg, decoder, content, style, alpha=1.0):
    """Performs style transfer to content based on style image.

    Args:
        vgg (torch.nn.Module): A feature extractor net.
        decoder (torch.nn.Module): A net to decode extracted features.
        content (torch.Tensor): The image to get content from.
        style (torch.Tensor): The image to get style from.
        alpha (float): A parameter to tune style transfer strength.

    Returns:
       torch.Tensor.
       Stylized image.
    """
    content_f = vgg(content)
    style_f = vgg(style)
    feat = adaptive_instance_normalization(content_f, style_f)
    feat = feat * alpha + content_f * (1 - alpha)
    return decoder(feat)
