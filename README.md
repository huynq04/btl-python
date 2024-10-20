
## Với truy vấn nhiều điều kiện như này thì truy vấn có mất thời gian không?
## db có duyệt tất cả các record không?

member = (db.query(Member).filter(Member.group_id == post.group_id)
              .filter(Member.user_id == current_user.user_id, Member.status == 2)
              .first())