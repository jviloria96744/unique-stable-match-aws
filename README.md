# Unique Stable Match Simulations

This project contains source code and supporting files for an application that simulates and finds matching markets possessing a unique stable match.

The notion of matching markets and a unique stable match both come from the Matching literature in Economics, Mathematics and Computer Science. The canonical problem is known as the [Stable Marriage Problem](https://en.wikipedia.org/wiki/Stable_marriage_problem) and one of the most known results in this field is the one given by the [Gale-Shapley Algorithm](https://en.wikipedia.org/wiki/Gale%E2%80%93Shapley_algorithm) which provides a method for finding a stable match given a market.

## Project Description

This project includes an implementation of the Gale-Shapley Algorithm as well as functions to simulate a marriage market.

We simulate markets in a cascading procedure described below,

- Initially simulate a number of seed markets

- Use those seed markets in parallel to simulate more markets

- Apply the Gale-Shapley Algorithm to determine if there is a unique stable match. For those aware of the literature, we apply it twice, firm-proposing and worker-proposing, and see if the resulting stable matches are equal.

- In the event of a market possessing a unique stable match, we write that market object to a DynamoDB table

The parallelization is achieved by a Lambda function generating the seed markets and sending them to an SQS queue. Lambda functions acting as consumers of the queue then receive the messages and sample more markets as well as apply the Gale-Shapley Algorithm, writing the results to DynamoDB if necessary
