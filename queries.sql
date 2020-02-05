--load posts
/* posts = array : 
post_id, text, date, likes_count, dislikes_count, comments_count, 
if_liked_by_user, if_disliked_by_user, owner: User, */


SELECT  p.post_id, p.text, p.date, IFNULL(COUNT(pl.post_id), 0),
        IFNULL(COUNT(pdl.post_id), 0),
        IFNULL(COUNT(c.post_id), 0)
FROM    posts p, users u, post_likes pl, post_dislikes pdl,
        post_comments c
WHERE   p.post_id = pl.post_id (+)
AND     p.post_id = pdl.post_id (+)
AND     p.post_id = c.post_id (+)
GROUP BY p.post_id

sdsdsd

sdsdsdsdsdsd