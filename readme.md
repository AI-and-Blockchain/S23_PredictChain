# PredictChain

PredictChain is a marketplace for predictive AI models. Users will be able to upload datasets
to train predictive models, or submit queries to those models.  These various models will be 
operated by a central node or nodes with computing resources available. A variety of models will be 
made available, ranging from cheap, fast, and simple to more expensive, slower, and more powerful. 
This will allow for a large variety of predictive abilities for both simple and complex patterns.
All the past predictions form these models will be stored on the blockchain for public viewing.

## User Actions

Users can interact with this system through a variety of ways.  Users can choose to upload datasets
of their own, train one of the base models on any previously uploaded dataset, or query any of the
trained models for a specific result.

## Model Classes

There will be several types of models available for use.  These may include:

- Decision Trees
- Multi-layered Perceptrons
- Linear Neural Networks
- Recurrent Neural Networks

The capabilities of these different methods varies greatly.  To save on costs, users with simple
classification tasks can opt for models that are cheaper, but will still provide good results.
Alternatively, users looking to analyze more complex relations can select the more complex models
at a higher cost.  Users are incentivized to balance cost and performance as they will be rewarded
for better performing models.

## The Oracle

The oracle is a privileged node that helps the blockchain keep up to date with the outside world.
It can help get information out of the blockchain and to a programmatic API, or it can gather 
information from the outside world and inject it back into the blockchain.  For example, it would
listen for the outcomes of user-predicted events and return those results to the users and update
those who submitted the dataset.

Communication between the blockchain and the oracle is facilitated by transactions.  When a message
needs to be sent between the two parties, the sending party creates a transaction with a note attached.
This note contains a json-encoded form of the arguments for the operation being requested.  These 
arguments are then received and interpreted by the target of the transaction.

## Payments and Incentives

Payments and incentives help to turn this project into a functioning system.  They are each calculated
using a fixed equation that is open to all users to view.  Each reward and incentive is also subject to
a multiplier.  This can be raised or lowered by the oracle at any point.  To ensure there is a
constant log kept in the blockchain, the id of this modifying transaction will be saved and returned
to any user upon request.

### Payments
- Any user will be able to query previously trained models for predictions of real-world events.
Each time this is done, these users will make a small payment to the system.

- Users who upload their own datasets will also have to pay a small fee.  This fee is based off of
the size of the dataset that they plan to upload.

 - Users who choose to request that a base model be trained on a particular dataset will also be
charged with a small fee.  This fee is based off of a variety of factors including the complexity
of the model and the size of the dataset.

### Incentives

To compensate for the payments that users make to the system, they will also be rewarded in the right
circumstances.

- Dataset uploading users will be rewarded both when a model is trained on their dataset and when
that trained model makes a correct prediction.

- Model training users will be rewarded whenever their model makes a correct prediction.

- Each of the predictions mentioned above are triggered when a user queries the model for some event.

## User Interface Wireframes

![UIWireframe](img/PredictChainLanding.png)

![UIWireframe](img/PredictChainPortfolio.png)

## Diagrams

### Sequence Diagram

![Sequence Diagram](img/PredictChainSequence.png)

### Use Case Diagram

![Sequence Diagram](img/PredictChainUseCase.png)
