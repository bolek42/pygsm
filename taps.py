from gnuradio import gr
import Gnuplot, Gnuplot.funcutils
from math import *

g = Gnuplot.Gnuplot(debug=1)
g('set style data lines')

filter_cutoff   = 145e3
filter_t_width  = 10e3
#x = gr.firdes.low_pass(1.0, 16e6, filter_cutoff, filter_t_width, gr.firdes.WIN_HAMMING)

def gauss( x):
    my = 0
    sigma = 0.5

    y = exp( -0.5 * ((x - my) / sigma)**2)
    y *= (1.0/ (sigma * sqrt( 2*pi)))

    return y

def gauss_int( x):
    y = 0
    x_i = -10
    d_x = 0.01
    while x_i < x:
        y += gauss( x_i) * d_x
        x_i += d_x

    return y

def f(x, l):
    x = -abs(x - (l / 2.0))
    x = x / 10.0 + 8
    return gauss_int( x)

x = []
for i in range( 200):
    print i
    y = f(i, 200)
    x.append( y)

print x
g.plot(x)

a = raw_input("")
raw_input()
