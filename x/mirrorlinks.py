# def mirror_symlinks(src: str, dst: str) -> None:
#     def mirror_link(lp: str) -> None:
#         check.state(os.path.islink(lp))
#         shutil.copy2(
#             lp,
#             os.path.join(dst, os.path.relpath(lp, src)),
#             follow_symlinks=False,
#         )
#
#     for dp, dns, fns in os.walk(src, followlinks=False):
#         for fn in fns:
#             mirror_link(os.path.join(dp, fn))
#
#         for dn in dns:
#             dp2 = os.path.join(dp, dn)
#             if os.path.islink(dp2):
#                 mirror_link(dp2)
#             else:
#                 os.makedirs(os.path.join(dst, os.path.relpath(dp2, src)))

current_link = os.path.join(home, 'deploys/current')

# if os.path.exists(current_link):
#     mirror_symlinks(
#         os.path.join(current_link, 'conf'),
#         conf_tag_dir,
#     )
#     mirror_symlinks(
#         os.path.join(current_link, 'apps'),
#         os.path.join(deploy_dir, 'apps'),
#     )
