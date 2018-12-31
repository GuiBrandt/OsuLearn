def bsearch(list, target, func):
	i = 0

	beg = 0
	end = len(list)

	while end > beg:
		i = (end + beg) // 2
		obj_time = func(list[i])

		if obj_time > target:
			end = i - 1
		elif obj_time < target:
			beg = i + 1
		else:
			break
	return i