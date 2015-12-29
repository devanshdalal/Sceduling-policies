### Scheduling Policies
==============================

Baadal is the IIT Delhi academic cloud on which Virtual Machines (VMs)
are run. Currently it is using the first fit strategy for scheduling the
VMs on the Physical Machines (PMs). Our current work focusses on
improving the scheduling capacity for Baadal. We then provide analysis
of a simulation we used in evaluating the different strategies.

### Currently implemented Strategy
==============================
When a new request for a Virtual Machine comes in, it has associated
with it the parameters - CPU (cores needed) and RAM. It is then placed
using the First Fit strategy in the first host that meets the
requirements of the new VM, after sorting the hosts in the order of
total RAM.

When the user changes the level of a VM and restarts it, it is placed
again in a new host following the same strategy as above.

### Improvements
============
1.  <span> It can be proven that online first fit for 2-dimentional
    packing is O(d)-competitive and will not use more than 2.7 times the
    optimal number of bins packed offline. @Garey1976 </span>

2.  <span>While sceduling a new Vm by First Fit, the host list is sorted
    in decreasing order of their weighted sum of usedRam and usedCpu.
    This is done in order to fit the new requests in highly filled hosts
    for compact packing.</span>

3.  <span>In the improved strategy we run a particular function(*help*)
    at regular intervals which tries to shut down the least utilized
    host(*victim*) if it can be done by migrating the Vms on it to other
    hosts(*targets*) .</span>

4.  <span>The help function tries to fit the victim’s Vms given as a
    list to other host either directly if possible or by removing
    removing smaller Vms from target hosts and adding these next level
    Vms to the input list and continuing the loop uptill 2 or three
    levels. </span>

Analysis
========
-   <span>For comparing various strategies we generate a list of queries
    for the simulation, where a query can be a request for a new Vm ,
    change the level of any existing Vm or delete a Vm while maintaining
    the average number of new Vms and deleted Vms equal. </span>

-   <span>The policies used for scheduling are first fit,best fit,
    random fit as shown in the plot, the integer 2 is added as suffix
    for the improved corresponding algorithm( i.e. migration included).
    </span>

-   The average number of hosts used by each policy are ploted in the
    graph shown below.

<!--     ![Simulation Results]()

-   ![Initial State of Vms and Hosts](h1)

    ![Host 51 shut down and its Vms migrated to other hosts](h2) -->

-   <span> We have also used migration if first fit fails to schedule a
    request to decrease the rejected requests during the simulation. The
    number of requests rejected for a list of 10,000 request were only
    370 as compared to 665 without migration. </span>


------
Title: 'Scheduling policies for Baadal - the IITD cloud'
Authors:
- Nishant Kumar
- Devansh Dalal <br>
...

## Credits
----------------
[Devansh Dalal](https://github.com/devanshdalal) <br>
[Nishant Kumar](https://github.com/nish_kr) <br>


### Screenshots
----------------
![s](https://cloud.githubusercontent.com/assets/5080310/13222407/c69910f6-d9a5-11e5-902a-1195cfb6ab62.png)
----------------
![s](https://cloud.githubusercontent.com/assets/5080310/13222411/c6b9594c-d9a5-11e5-959b-8f9b481f4843.png)
----------------
![s](https://cloud.githubusercontent.com/assets/5080310/13222393/c6322616-d9a5-11e5-8c78-a9d68114ca9a.jpg)
----------------