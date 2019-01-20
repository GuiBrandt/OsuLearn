OsuLearn
========
### An attempt at creating a Neural Network that learns how to play osu!std like a human from replays
###### (Plz don't judge me too much I'm new to machine learning and i can't english)

Introduction
------------

> osu! is a free and open-source rhythm game developed and published by Australian-based company PPY Developments PTY, created by Dean Herbert (also known as peppy). Originally released for Microsoft Windows on September 16, 2007, the game has also been ported to macOS (this version might be unstable), and Windows Phone. Its gameplay is based on titles including Osu! Tatakae! Ouendan, Elite Beat Agents, Taiko no Tatsujin, Beatmania IIDX, O2Jam, and DJMax. 
>
> -- <cite>[Wikipedia](https://en.wikipedia.org/wiki/Osu!)</cite>

The goal here is to model and train a Neural Network to generate replays for any osu beatmap it is given based on a dataset of recorded human replays (`.osr` files) and their respective beatmap (`.osu`) file.

To accomplish that, I've trained a Recurrent Neural Network with my replays and beatmaps.

Results
-------

This is a preview for a replay generated for a map the AI had never seen before:

![IA Generated Replay](https://media.giphy.com/media/1wn8SVlutuiIxJ88Oi/giphy.gif)

Pretty good, actually!

It has figured out how to aim without looking like a robot and can even hit some jumps. Of course it is not perfect, but neither is the data set it has been trained on, so I am considering this a success.

Future
------

The next step is to transform this into a GAN, so it can generate multiple different replays for a given map, mimicking a human play style.

This might take some time though, so that's it for now x).