import math
import os.path
import typing as ta

import numpy as np
import sklearn.neighbors


Embedding: ta.TypeAlias = np.ndarray


class VecStore:
    def __init__(
            self,
            embed: ta.Callable[[ta.Any], Embedding],
    ) -> None:
        super().__init__()
        self._embed = embed

        self._neighbors = sklearn.neighbors.NearestNeighbors(metric='cosine')

        self._embeddings: list[Embedding] = []
        self._items: list[ta.Any] = []

        self._embeddings_np: ta.Any = np.asarray([])

    def _compute(self) -> None:
        self._embeddings_np = np.stack(self._embeddings, axis=0)
        self._neighbors.fit(self._embeddings_np)

    def add_items(self, items: ta.Iterable[ta.Any]) -> None:
        items = list(items)
        embs = self._embed(items)
        self._items.extend(items)
        self._embeddings.extend(embs)
        self._compute()

    def search(self, query: ta.Any, k: int = 1) -> list[tuple[ta.Any, float]]:
        query_embedding = self._embed([query])[0]
        neigh_dists, neigh_idxs = self._neighbors.kneighbors([query_embedding], n_neighbors=k)
        return [(self._items[idx], dist) for idx, dist in zip(neigh_idxs[0], neigh_dists[0])]


def _main() -> None:
    from PIL import Image
    images: list[Image] = []
    max_images = 500
    img_dir = os.path.expanduser('~/Downloads/yelp/photos')
    for fn in sorted(os.listdir(img_dir)):
        if not fn.endswith('.jpg'):
            continue
        print(fn)
        images.append(Image.open(os.path.join(img_dir, fn)))
        if len(images) >= max_images:
            break

    height = 512
    width = 512

    # mode = 'sd'
    # mode = 'pca'
    mode = 'clip'

    if mode == 'pca':
        def prep_img(img):
            img = img.resize((width, height))
            img = np.array(img)
            return img[:, :, :3]

        def prep_img_t(img):
            img = prep_img(img)
            img = np.mean(img, axis=2)
            img = img.reshape(-1)
            return img

        from sklearn.decomposition import PCA
        p_imgs = np.stack([prep_img_t(img) for img in images])
        pca = PCA(n_components=384)
        pca.fit(p_imgs)

        def embed(imgs: list[Image]) -> list[Embedding]:
            return list(pca.transform([prep_img_t(i) for i in imgs]))

    elif mode == 'sd':
        import torch
        torch.no_grad().__enter__()

        device = 'mps'

        from stable_diffusion_pytorch import util

        def prep_img_t(img):
            img_t = torch.tensor(prep_img(img), dtype=torch.float32)
            img_t = util.rescale(img_t, (0, 255), (-1, 1))
            img_t = img_t.permute(2, 0, 1)
            return img_t

        from stable_diffusion_pytorch import model_loader
        encoder = model_loader.load_encoder(device)

        def embed(imgs: list[Image]) -> list[Embedding]:
            embs = []
            bs = 8
            noise = torch.Tensor(np.zeros((bs, 4, height // 8, width // 8))).to(device)
            for n in range(math.ceil(len(imgs) / bs)):
                b = imgs[n * bs:(n + 1) * bs]
                img_ts = [prep_img_t(img) for img in b]
                inp = torch.stack(img_ts, axis=0)
                emb = encoder(inp.to(device), noise.to(device))
                embs.extend([e.flatten().cpu().detach().numpy() for e in emb])
            return embs

    elif mode == 'clip':
        import torch
        torch.no_grad().__enter__()

        from transformers import CLIPProcessor, CLIPModel
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        from stable_diffusion_pytorch import util

        def prep_img_t(img):
            img_t = torch.tensor(prep_img(img), dtype=torch.float32)
            img_t = util.rescale(img_t, (0, 255), (-1, 1))
            img_t = img_t.permute(2, 0, 1)
            return img_t

        def embed(imgs: list[Image]) -> list[Embedding]:
            embs = []
            for img in imgs:
                inputs = processor(images=img, return_tensors="pt", padding=True)
                outputs = model(**inputs)
                embs.append(outputs.image_embeds)
            return embs

    else:
        raise ValueError(mode)

    vs = VecStore(embed)
    vs.add_items(images[1:])

    q = images[0]
    res = vs.search(q, 3)
    q.save('q.png')
    for i, (r, d) in enumerate(res):
        print(d)
        r.save(f'r{i}.png')


if __name__ == '__main__':
    _main()
