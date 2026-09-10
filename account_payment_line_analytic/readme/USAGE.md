1.  Set an *Analytic Distribution* on a payment header.
2.  Add counterpart lines. The lines with no analytic distribution inherit the
    one from the payment; lines with their own distribution keep it.
3.  On post, each counterpart journal item carries the distribution of its
    line.
