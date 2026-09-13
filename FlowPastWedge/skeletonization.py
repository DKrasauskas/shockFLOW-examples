import argparse
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from skimage import color, filters, img_as_float, io
from skimage.morphology import (
    dilation,
    disk,
    remove_small_holes,
    remove_small_objects,
    skeletonize,
)

# Distinct colors used to tell multiple skeletons apart when overlaid together.
# Extend this list if you have more than 8 cases.
DEFAULT_PALETTE = [
    (0, 0, 127), (0, 16, 255), (0, 164, 255), (63, 255, 183),
    (183, 255, 63), (255, 185, 0), (255, 48, 0), (127, 0, 0),
]


def load_skeleton(path, threshold=40):
    """Load a previously saved skeleton PNG (or any image) as a boolean mask."""
    img = io.imread(path)
    if img.ndim == 3:
        img = color.rgb2gray(img[..., :3]) * 255
    return img > threshold


def draw_legend(img, labels, colors=None, loc="upper right", font_size=16, margin=10, box_alpha=160):
    """
    Draw a color-swatch legend onto an (H, W, 3) uint8 image and return a
    new (H, W, 3) uint8 array with the legend composited on top.

    labels : list of strings, one per skeleton/color, in the same order the
        skeletons were passed to overlay_on_background().
    colors : list of (R, G, B) 0-255 tuples matching labels. Defaults to
        DEFAULT_PALETTE.
    loc : one of "upper right", "upper left", "lower right", "lower left".
    font_size : legend text size in points.
    margin : padding in pixels around the legend box and between its rows.
    box_alpha : opacity (0-255) of the legend's translucent background box,
        so labels stay readable regardless of what's underneath.
    """
    if colors is None:
        colors = DEFAULT_PALETTE
    if loc not in ("upper right", "upper left", "lower right", "lower left"):
        raise ValueError(
            f"Unknown loc '{loc}'. Use one of: upper right, upper left, lower right, lower left."
        )

    base = Image.fromarray(img).convert("RGBA")
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = ImageFont.load_default(size=font_size)

    swatch = font_size
    text_pad = 8
    row_h = swatch + 6

    max_text_w = max(draw.textlength(str(lbl), font=font) for lbl in labels)
    box_w = int(margin * 2 + swatch + text_pad + max_text_w)
    box_h = int(margin * 2 + row_h * len(labels))

    W, H = base.size
    if loc == "upper right":
        x0, y0 = W - box_w - margin, margin
    elif loc == "upper left":
        x0, y0 = margin, margin
    elif loc == "lower right":
        x0, y0 = W - box_w - margin, H - box_h - margin
    else:  # lower left
        x0, y0 = margin, H - box_h - margin

    draw.rounded_rectangle([x0, y0, x0 + box_w, y0 + box_h], radius=6, fill=(0, 0, 0, box_alpha))

    for i, label in enumerate(labels):
        cy = y0 + margin + i * row_h
        col = tuple(colors[i % len(colors)])
        draw.rectangle([x0 + margin, cy, x0 + margin + swatch, cy + swatch], fill=col + (255,))
        draw.text((x0 + margin + swatch + text_pad, cy - 1), str(label), font=font, fill=(255, 255, 255, 255))

    return np.array(Image.alpha_composite(base, layer).convert("RGB"))


def overlay_on_background(
    background,
    skeletons,
    colors=None,
    alpha=1.0,
    dilate=0,
    labels=None,
    legend_loc="upper right",
    legend_font_size=16,
):
    """
    Composite one or more shock skeletons on top of a background image.

    background : str/PathLike path to an image, or an already-loaded array.
        The base canvas. Must have the same (height, width) as the skeletons
        -- it can be one of your original source images, or any other
        reference image (photo, schematic, CAD drawing, etc.) of matching
        resolution.
    skeletons : a single boolean skeleton array, a path to a saved skeleton
        PNG, or a list mixing either -- e.g.
            process_images(...)[path]["skeleton"]
        or
            load_skeleton("mach2.0_skeleton.png")
    colors : list of (R, G, B) 0-255 tuples, one per skeleton. Defaults to
        DEFAULT_PALETTE.
    alpha : float in [0, 1]. Opacity of the skeleton lines over the
        background (1.0 = fully opaque line color, 0.5 = half blended).
    dilate : int. Thickens skeleton lines by this many pixels of radius so
        1px-wide lines stay visible over a busy background. 0 = no
        thickening (draw exact 1px skeleton).
    labels : optional list of strings, one per skeleton, in the same order
        as `skeletons` (e.g. ["Mach 1.5", "Mach 2.0"]). If given, a legend
        with a color swatch + label per skeleton is drawn onto the result.
    legend_loc : one of "upper right" (default), "upper left", "lower right",
        "lower left". Where to place the legend box.
    legend_font_size : legend text size in points. Default 16.

    Returns the composited image as an (H, W, 3) uint8 array.
    """
    bg = io.imread(background) if isinstance(background, (str, os.PathLike)) else background
    bg = img_as_float(bg)
    if bg.ndim == 2:
        bg = color.gray2rgb(bg)
    elif bg.shape[-1] == 4:
        bg = bg[..., :3]

    if isinstance(skeletons, (np.ndarray, str, os.PathLike)):
        skeletons = [skeletons]
    skel_arrays = [load_skeleton(s) if isinstance(s, (str, os.PathLike)) else s for s in skeletons]

    for s in skel_arrays:
        if s.shape != bg.shape[:2]:
            raise ValueError(
                f"Skeleton shape {s.shape} does not match background shape {bg.shape[:2]}."
            )

    if colors is None:
        colors = DEFAULT_PALETTE

    if labels is not None and len(labels) != len(skel_arrays):
        raise ValueError(
            f"Got {len(labels)} labels but {len(skel_arrays)} skeletons; they must match 1:1."
        )

    out = bg.copy()
    for i, s in enumerate(skel_arrays):
        if dilate > 0:
            s = dilation(s, footprint=disk(dilate))
        col = np.array(colors[i % len(colors)], dtype=float) / 255.0
        out[s] = (1 - alpha) * out[s] + alpha * col

    out = (np.clip(out, 0, 1) * 255).astype(np.uint8)

    if labels is not None:
        out = draw_legend(out, labels, colors=colors, loc=legend_loc, font_size=legend_font_size)

    return out


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _basename_no_ext(path):
    return os.path.splitext(os.path.basename(path))[0]


def process_images(
    image_paths,
    outdir="shock_skeletons",
    percentile=42.0,
    min_abs=0.0,
    min_size=40,
    prune_len=18,
    sigmas=(1, 2, 3, 4),
    overlay=False,
    background=None,
    alpha=1.0,
    dilate=0,
    labels=None,
    legend_loc="upper right",
    legend_font_size=16,
):
    """
    Run the shock-skeletonization pipeline on one or more images and write
    the results to `outdir`. This is the function to call directly if you
    want to use the pipeline from another script or a notebook, e.g.:

        from shock_skeletonize import process_images
        process_images("mach2.0.png")
        process_images(["mach1.5.png", "mach2.0.png"], overlay=True)
        process_images(["mach1.5.png", "mach2.0.png"], overlay=True,
                        background="mach1.5.png", alpha=0.9, dilate=1,
                        labels=["Mach 1.5", "Mach 2.0"])

    Parameters
    ----------
    image_paths : str, os.PathLike, or list of them
        A single image path, or a list of image paths that must all share
        the same resolution.
    outdir : str
        Directory to write outputs into (created if it doesn't exist).
    percentile, min_abs, min_size, prune_len, sigmas
        See skeletonize_shocks() / the CLI --help text for details.
    overlay : bool
        If True, also write outdir/overlay.png with each image's skeleton
        drawn in a distinct color.
    background : str, os.PathLike, or None
        If given, the combined overlay is composited on top of this image
        instead of a black canvas -- e.g. pass one of your original source
        images (or any other reference image of the same resolution) to see
        the extracted shocks superimposed on real image content. Only used
        when overlay=True.
    alpha : float in [0, 1]
        Opacity of the skeleton lines when a background is used. Default 1.0
        (fully opaque lines).
    dilate : int
        Thicken skeleton lines by this many pixels of radius before drawing,
        so thin 1px lines stay visible over a busy background. Default 0.
    labels : optional list of strings, one per input image, in the same
        order as `image_paths` (e.g. ["Mach 1.5", "Mach 2.0"]). If given,
        a legend with a color swatch + label per image is drawn onto the
        overlay. Only used when overlay=True.
    legend_loc : one of "upper right" (default), "upper left", "lower right",
        "lower left". Where to place the legend box.
    legend_font_size : legend text size in points. Default 16.

    Returns
    -------
    dict mapping each input path -> {"skeleton": array, "mask": array}
    """
    if isinstance(image_paths, (str, os.PathLike)):
        image_paths = [image_paths]

    os.makedirs(outdir, exist_ok=True)

    ref_shape = None
    skels_in_order = []
    results = {}

    for i, path in enumerate(image_paths):
        img = io.imread(path)

        if ref_shape is None:
            ref_shape = img.shape[:2]
        elif img.shape[:2] != ref_shape:
            raise ValueError(
                f"'{path}' has shape {img.shape[:2]}, expected {ref_shape}. "
                "All input images must share the same resolution."
            )

        skel, mask, ridge, lum = skeletonize_shocks(
            img,
            ridge_sigmas=sigmas,
            percentile=percentile,
            min_abs=min_abs,
            min_size=min_size,
            prune_len=prune_len,
        )

        name = _basename_no_ext(path)
        io.imsave(
            os.path.join(outdir, f"{name}_skeleton.png"),
            (skel * 255).astype(np.uint8),
            check_contrast=False,
        )
        io.imsave(
            os.path.join(outdir, f"{name}_mask.png"),
            (mask * 255).astype(np.uint8),
            check_contrast=False,
        )
        print(f"[{i+1}/{len(image_paths)}] {path}: {skel.sum()} skeleton pixels")
        results[path] = {"skeleton": skel, "mask": mask}
        skels_in_order.append(skel)

    if overlay and skels_in_order:
        if labels is not None and len(labels) != len(skels_in_order):
            raise ValueError(
                f"Got {len(labels)} labels but {len(skels_in_order)} input images; "
                "they must match 1:1, in the same order."
            )
        canvas = background if background is not None else np.zeros(ref_shape + (3,), dtype=np.uint8)
        overlay_img = overlay_on_background(
            canvas, skels_in_order, alpha=alpha, dilate=dilate,
            labels=labels, legend_loc=legend_loc, legend_font_size=legend_font_size,
        )
        out_path = os.path.join(outdir, "overlay.png")
        io.imsave(out_path, overlay_img, check_contrast=False)
        print(f"Overlay saved to {out_path}")

    return results



if __name__ == "__main__":
    skeleton1 = load_skeleton("/home/dominykas/Desktop/shockFlowProject/FlowPastWedge/Videos/last1.png")
    skeleton2 = load_skeleton("/home/dominykas/Desktop/shockFlowProject/FlowPastWedge/Videos/last2.png")
    skeleton3= load_skeleton("/home/dominykas/Desktop/shockFlowProject/FlowPastWedge/Videos/last3.png")
    skeleton4= load_skeleton("/home/dominykas/Desktop/shockFlowProject/FlowPastWedge/Videos/last4.png")
    skeleton5= load_skeleton("/home/dominykas/Desktop/shockFlowProject/FlowPastWedge/Videos/last5.png")
    skeleton6= load_skeleton("/home/dominykas/Desktop/shockFlowProject/FlowPastWedge/Videos/last6.png")
    skeleton7= load_skeleton("/home/dominykas/Desktop/shockFlowProject/FlowPastWedge/Videos/last7.png")
    skeleton8= load_skeleton("/home/dominykas/Desktop/shockFlowProject/FlowPastWedge/Videos/last8.png")

    labels = ["Mach 1.1", "Mach 1.2", "Mach 1.4", "Mach 1.6", "Mach 1.8", "Mach 2.0 ", "Mach 2.2",  "Mach 2.4"]
    combo = overlay_on_background(
        "/home/dominykas/Desktop/shockFlowProject/FlowPastWedge/Videos/last1.png",
        [skeleton1, skeleton2, skeleton3, skeleton4, skeleton5, skeleton6, skeleton7, skeleton8],
        labels=labels,
        legend_font_size=16,
        legend_loc="upper right",
        alpha=0.9, dilate=1,
    )
    io.imsave("combined_overlay3.png", combo, check_contrast=False)