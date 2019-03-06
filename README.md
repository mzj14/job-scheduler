# job-scheduler
Multiple-Producer-Single-Consumer Job Scheduler

## Question
```
Suppose that you need to implement a job scheduler that takes incoming jobs with the spec (start, interval) and stores the jobs in an internal queue.
Then it runs the jobs repeatedly(adinfinitum) until they are removed from the scheduler. For example, someone may use the following code to use such a
queue.

Runnable job1, job2;
RepeatingJobQueue queue = RepeatingJobQueue();
queue.addJob(job1, start1, interval1);
.....
queue.addJob(job2, start2, interval2); // some other thread
queue.removeJob(job2);

How would you implement RepeatingJobQueue? Articulate the assumptions you are making in order for your code to work.
```
## Analysis
It is a multiple-producer-single-consumer problem. Each time we call `addJob`, we have a new producer created to periodically put new job instance to a shared job instance queue. Meanwhile, we have a global consumer which constantly gets the head item in the job instance queue and launch this instance in the background.

We use python3 to solve this problem. We hereby point out key skills in our solution.

* We use `threading.Thread` & `threading.Event` module to help create/stop producer thread in `addJob`/`removeJob`, as well as create the global consumer at the beginning.

* We use `thread.Condition` to let producer/consumer acquire/release lock when they manipulate the shared job instance queue.

* We use `thread.Condition` to let the consumer pause when the queue is empty and producers to notify the consumer when they put new items in the queue.

## Solution
Run
```
./scheduler.py [job_num] [insert_interval] [launch_delay] [launch_interval] [full_run_time]
```
where
* job_num: # of jobs, whose ids start from 0
* insert_interval: interval between current `addJob`/`remove` call and the next one
* launch_delay: the delay from `addJob` call to the time when the first instance of the job is launched
* launch_interval: interval between launching the current instance and the next one
* full_run_time: duration from completing adding all jobs to the time when removing jobs begins.

For example,
```
./scheduler.py 3 1 1 2 10
```
would gives the following output:
```
start instance 1 of job 0 in background at unix timestamp 1551911581
start instance 1 of job 1 in background at unix timestamp 1551911582
start instance 2 of job 0 in background at unix timestamp 1551911583
start instance 1 of job 2 in background at unix timestamp 1551911583
start instance 2 of job 1 in background at unix timestamp 1551911584
start instance 2 of job 2 in background at unix timestamp 1551911585
start instance 3 of job 0 in background at unix timestamp 1551911585
start instance 3 of job 1 in background at unix timestamp 1551911586
start instance 3 of job 2 in background at unix timestamp 1551911587
start instance 4 of job 0 in background at unix timestamp 1551911587
start instance 4 of job 1 in background at unix timestamp 1551911588
start instance 4 of job 2 in background at unix timestamp 1551911589
start instance 5 of job 0 in background at unix timestamp 1551911589
start instance 5 of job 1 in background at unix timestamp 1551911590
start instance 5 of job 2 in background at unix timestamp 1551911591
start instance 6 of job 0 in background at unix timestamp 1551911591
start instance 6 of job 1 in background at unix timestamp 1551911592
start instance 6 of job 2 in background at unix timestamp 1551911593
```
which stands for the following scheduling:

| Time Slot   | 0   | 1   | 2   | 3   |4   | 5   | 6   | 7   | 8   | 9   | 10   | 11   |12   |
| :----------:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Job 0       | X    |     |   X  |     |  X   |     |  X   |     |  X   |     |   X  |     |     |
| Job 1       |     |  X   |     |  X   |     |   X  |     |  X   |     |   X  |     |   X  |     |
| Job 2       |     |     |   X  |     |   X  |     |  X   |     |  X   |     |  X   |     |  X   |

## Hint
Comments are welcomed.
