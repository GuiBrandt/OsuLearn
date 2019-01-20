def _print_progress_bar(collection, index, bar_width=40, buffer_width=80, reverse=False):
    bar_format = "\r[{done}>{todo}] {text}"

    progress = index / (len(collection) - 1)
    if reverse:
        progress = 1 - progress

    bar_raw_length = len(bar_format.format(done='', todo='', text=''))
    done = int(round(progress * bar_width))

    text = str(collection[index])
    if len(text) > buffer_width - bar_raw_length - bar_width:
        text = text[:buffer_width - bar_raw_length - bar_width - 3] + '...'

    print(bar_format.format(
        done='=' * (done - 1),
        todo='.' * (bar_width - done),
        text=text).ljust(buffer_width), end='')