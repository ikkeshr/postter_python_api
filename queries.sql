post_id, text, date, likes_count, dislikes_count, 
comments_count, if_liked_by_viewer, if_disliked_by_viewer, if_own_by_viewer, 
user_id, username, profile_pic_url

--params: _sortby, _offset, _limit, _viewer_user_id

SELECT      p.post_id, p.text, p.date, 
            ple.likes_count, pdle.dislikes_count, pce.comments_count,
            vlp.if_liked_by_viewer, vdlp.if_disliked_by_viewer, vp.if_own_by_viewer,
            u.user_id, u.username, u.profile_pic_url

FROM        posts p, users u,
            (
                SELECT      p.post_id, COUNT(pl.post_id) as likes_count
                FROM        posts p LEFT JOIN post_likes pl ON p.post_id=pl.post_id
                GROUP BY    p.post_id
            ) as ple,
            (
                SELECT      p.post_id, COUNT(pdl.post_id) as dislikes_count
                FROM        posts p LEFT JOIN post_dislikes pdl ON p.post_id=pdl.post_id
                GROUP BY    p.post_id
            ) as pdle,
            (
                SELECT      p.post_id, COUNT(pc.post_id) as comments_count
                FROM        posts p LEFT JOIN post_comments pc ON p.post_id=pc.post_id
                GROUP BY    p.post_id
            ) as pce,
            (
                SELECT      post_id, IF(owner_user_id=%(viewer_user_id)s, 1, 0) as if_own_by_viewer
                FROM        posts 
            ) as vp,
            (
                SELECT      p.post_id, COUNT(pl.post_id) as if_liked_by_viewer
                FROM        posts p LEFT JOIN post_likes pl ON p.post_id=pl.post_id AND pl.user_id=%(viewer_user_id)s
                GROUP BY    p.post_id
            ) as vlp,
            (
                SELECT      p.post_id, COUNT(pdl.post_id) as if_disliked_by_viewer
                FROM        posts p LEFT JOIN post_dislikes pdl ON p.post_id=pdl.post_id AND pdl.user_id=%(viewer_user_id)s
                GROUP BY    p.post_id
            ) as vdlp

WHERE       p.post_id = ple.post_id
AND         p.post_id = pdle.post_id
AND         p.post_id = pce.post_id
AND         p.post_id = vlp.post_id
AND         p.post_id = vdlp.post_id
AND         p.post_id = vp.post_id
AND         p.owner_user_id = u.user_id