# Blog: Braikout

**Ross Franey**

## My First Blog Entry - Intro to Project

This is my first blog entry.

This blog has been created with the intention of documenting the procedure of the development of Braikout. 

Braikout is a forex and cryptocurrency trading platform which will make use of machine learning, chart analysis and sentiment analysis to predict the price action, 
potential buy/sell signals, and market sentiment of multiple digital and traditional currency markets. 



## My Second Blog Entry

### Introduction and GANT Chart

The initial GANT Chart for my project, excluding documentation and taking into account a short break during the Christmas holidays.
The GANT chart outlines my proposed timeline of completion for the various aspects involved in my project as I see them now, and is subject to change throughout the course of the project. Nonetheless it is a useful tool to help keep the various aspects involved in perspective and to manage time allocation appropriately.
I intend to update this chart, or create a separate GANT chart for documentation of this project in terms of the project proposal (complete), functional specification, technical specification, and testing documentation. 

![images](docs/blog/images/print.JPG)

## My Third Blog Entry

### Sentiment Analysis Decision

This week I have been establishing the basic user interface and examining the various ways in which I could implement sentiment analysis, starting with twitter. the two main ways I could approach this problem depend on how heavily I wish to focus my time on the sentiment analysis aspect of the project. The simple approach would require me to use TextBlob's library for python, and write roughly 14 lines of code, and would return two values, one to score the positivity of each tweet (polarity), and another to determine how factual / opinion-based the tweet is (subjectivity). Each of these would be separated into their own categories and the user could be given an idea of the general consensus, if one exists, on twitter for the specific market they are interested in. 
	
The second method involves using the NLTK library for python. This involves actually building my own analytical sentiment classifier in python, and using various files to train my own classifier to have better control of how it makes decisions and classifications. Although this would be far more work, it may afford me a better result than the previously mentioned method. This being said, it may not. 

I have decided the best option would be first to try the method I can run sooner, and build on it if need be. If I find it insufficient for my needs, I can switch and create my own classifier.


### UI Implementation

Another challenge I continue to face is becoming familiar with Python/Django. As I have no experience even in python let alone Django, development is slightly slower than it would be if I was making use of a more familiar language such as Java. This being said, I am enjoying familiarizing myself with the language and am confident that development will continuously get faster throughout the course of the project.


## Post-Holiday Updates & Plans

### Machine learning model 
Over the Christmas period, despite being distracted by studying for exams, I managed to work out all the small bugs in my application surrounding the new API that Bitstamp (cryptocurrency exchange) decided to use. As well as this, I have been searching for better ways to predict the next price on a day to day basis. Many of the datasets on Kaggle include a huge amount of small time frame information which is important for intra-day trading, but leads to a lot of noise when we try to predict daily price action.  
As a result, I have found that a more successful approach would be to pull market data live, directly from coinmarketcap.com. This means the application itself is more lightweight, and also that pricing is always up to date, rather than having to update a SQL database in bulk every *fixed time frame*.
At the moment, the price prediction is working from a random seeded regression model, where the seed is chosen based on experimentation. 
I will detail further the approach, alongside the one on which I am now working (which is using an LSTM), in the next blog post.

### Other fixes 
On a smaller technical note, I have logically separated forex coins from crypto coins, as well as considered the various fundamental factors that effect forex growth. This is particularly interesting as of today (26/01/18), because of the fall of the USD, with the world economic forum taking place in Davos this week, and president Donald Trump to speak on the matter later today. I will be specifically examining this news in relation to the charts in order to determine the most accurate approach to predicting the price action based on news such as that which will unfold today. 

### Plans going forward
Also of interest to me is considering predicting sentiment for markets. This may be out of scope of the project but something I would like to consider further down the line for this app. 

## Machine Learning Results
In terms of training the machine learning model, a simple approach is to split the training data in half, train it on the first half of the data set, and then test the trained model on the remaining half. The problem with this in terms of bitcoin is of course the recent spike in price to 20 thousand dollars. This had not occurred when I first embarked on this project and has lead to some interesting challenges which I am now overcoming.
Nevertheless, using this approach, the following graph illustrates the problem using this approach, with the purple color on the left representing my training data and the green on the right representing the test data:

![images](docs/blog/images/training.JPG)


To get an idea of the importance of a seed value, the following is a result of running the tests using completely random jumps, with very poor results.

![images](docs/blog/images/randomWalk.JPG)

Despite being able to find a Gamma for which this is more accurate, a much better approach when we come to actually using the same model for the six markets available on this application, will be an LSTM approach.

Experimenting with some random seed values leads to interesting results, to the point where it is tempting to search all seeds in a range for the closest correlations. Although not the solution I will be looking for, below is an example of a seed which works very well on the Ethereum chart and not so well on bitcoin.

![images](docs/blog/images/ethseed.JPG)

## LSTM Implementation
To implement the Long Short Term Memory (LSTM) network, I have made use of the python library Keras. The main reason for this was a result of research on various online research forums, which indicated that Keras has wide acceptance in both the academic and research community. 
The LSTM uses previous data on the three cryptocurrencies to predict the next day's closing price, and eventually will incorporate more complicated factors such as sentiment analysis and technical chart indicators. 
Data frames or "windows" are built, with the size of the window being representative of the number of days the model will take into account to produce its prediction.
There is a clear trade off here, in that more days included per window means less windows can be "fed" to the model. However, fewer days means that any longer term trends will not be accounted for.
The next step is to experiment with the window size in order to determine the optimal values, however from an intuitive perspective, I would expect cryptocurrencies for the most part to respond just fine to a smaller window, considering long term trends don't always seem to be indicative of future price action.
Forex currencies, which is the next goal in terms of LSTM network implementation, may require larger sizes.   
Another factor to consider is the number of neurons to place in the LSTM layer of the model. As machine learning is completely novel to me up until this point, further testing and research will be required in order to determine the most appropriate values. 
A small value (20) is initially being used, however this is more for the relatively fast runtime while in the testing/experimentation phase. 
Finally, the model is fed the data on which it should be trained, i.e., the closing price for the specific coin, as fetched from CoinMarketCap (in the case of cryptocurrencies)

### The Efficient Market Hypothesis

The Efficient Market Hypothesis (EMH) states that there are essentially no patterns at play/involved in the stock market. It assumes that the price of a stock is always fair for a given exchange, and always takes into account all relevant factors. This means that it is essentially impossible to "beat" the market, or, make more profit by selecting a stock to purchase based on either fundamental or technical analysis.
Many believe that this is even more true for cryptocurrencies, considering their speculative nature, and there are disagreements in the trading world as to whether or not they should be treated as a stock (as many technically are - Initial coin offerings - https://www.investopedia.com/terms/i/initial-coin-offering-ico.asp), a currency (as again, many technically are), or a commodity such as gold. 
Regardless, there are studies to suggest that the Efficient Market Hypothesis does not always accurately represent price action. 
S.Basu's publication in the Journal of Finance, June 1977, found that "The behavior of security prices over the 14 year period studied is, perhaps, not completely described by the efficient market hypothesis".

Although there may be a large degree of efficiency, companies such as J.P. Morgan and Goldman Sachs spend large amounts of money hiring and training data analysts, suggesting that there is an advantage, however small, to be had from attempting this kind of market analysis.


### What this means for our model

Considering the EMH, after the completion of the above process for each cryptocurrency (including optimizing for the appropriate parameters of window size and neurons), testing will be carried out by comparing the Error rate of the LSTM model's prediction, alongside the initial random walk, in the hopes that the former will provide a prediction which has a higher chance of being more accurate than random.

## Displaying Prediction Charts in the App - 01/02/2018
As of now, the basic implementation of the LSTM network is working for cryptocurrencies. I have decided to focus in the short term on displaying the graphs in the appropriate location within the application itself. This is partially to switch up the type of work (as I have been working on the LSTM aspect for many weeks now) and also so I can overcome any problems that may arise in this task so that when the LSTM network is fully complete, I can simply "plug it in" to my application UI. 
This task is proving difficult as the graphs are drawn in MathPloltLib, which was not developed with displaying on web pages in mind. This is even more complicated when you consider Django, and the need to actually store the graph as a value of the Coin's Django model. 
In order to achieve this, I will be looking into saving the file as a byte array, and storing the byte array in the model. This way, in the actual template I can render it as an image and display it in the appropriate location.
Also to be considered is the appropriate location for various charts. Originally I had planned to create a separate page/template for Machine learning predictions, however upon reflection it may be more intuitive to implement the chart for a given coin as an image which can be toggle to show/hide, on the page for trading the coin. Even still, I may also implement a separate page which contains further details and more graphs for a specific prediction.

## Synchronous tasks with Celery / Raspberry Pi server / Sentiment improvement - 05/02/2018:
In order to achieve a fresh machine learning prediction each day, there has to be a way to schedule the running of the model on updated data. 
There are a few different methods which are currently being considered, however one which is currently working is using asynchronous task scheduling with the Celery library.
This allows the scheduling of tasks based on certain conditions, including time/date, which is ideal for my needs.
The problem at the moment is that the server (in my case, I am using Redis), which acts as a callback, cannot be connected to from my IP address in student accommodation as the network is behind a proxy and I don't have control over the ports. 

However, this can be solved by testing the project on my mobile hotspot. 

I am also considering making use of a Raspberry pi server to handle this aspect of the project, as it would make the application itself more light weight and also allow for multiple processes to be carried out without the need to schedule tasks. This increases the complexity of the project but would also make it much closer to a production-like piece of software. 
This solution would also mean I could employ a failsafe/backup protocol, so if there was a problem with the server on the raspberry pi, I could automatically revert to a piece of code in the application itself in order to obtain the fresh data and make a prediction. 
Another problem encountered was adding Litecoin to the machine learning algorithm. The predictions were noticeably less accurate when considering Litecoin's prices. However, I expect this will be able to be solved by simply finding more accurate seeds for individual models. The five-day model is still performing worse than the single day prediction, as expected.

Finally, I am also working on improving sentiment analysis by also considering the current Long/Short positions on a market, which is has a huge improving impact, and something that definitely should have been employed from the beginning.

## Sockets Successfully Implemented - Redis/Celery/Channels/Daphne/ASGI - 11/02/2018

This sprint was extended until today(Sunday) in order to finish a task which I knew to be on the verge of completing. This task is using sockets to pull live prices of various markets, to my application, process the prices, and update the web page in a synchronous manner without needing to reload the page. 
When writing my functional specification for this project, I chose Python as it would be a new challenge, considering I had no experience with the language. At the time, one of the downsides identified was the lack of support for sockets. Unlike Java, Python requires multiple external libraries to make socket programming work, a task made even more complicated by Django. 

Firstly, I installed Redis. From Redis.io: “Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache and message broker. It supports data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs and geospatial indexes with radius queries. “

This is the server I will be using as a message broker for the application.

Next, I installed Channels.

I then downloaded ASGI which stands for Asynchronous Server Gateway Interface, the specification on which Channels and Daphne is built upon. Traditionally, a Django project will have a WSGI file. The ASGI file is a spiritual successor to this file, and allows multiple protocols rather than ONLY the asynchronous asycnio, like WSGI.

I then downloaded Daphne. Daphne is a HTTP, HTTP2, and Web Socket protocol server for ASGI and ASGI-HTTP, which was developed to power Django Channels. This allowed me to omit the URL prefix when determining Web Socket endpoints vs HTTP endpoints. 

Finally, I downloaded Celery. This is a distributed task scheduler for python which supports real time processing. Learning to program using Celery was very time consuming, but even more rewarding, as the power it provides in terms of being able to process real time prices for alerts, pattern detection, identification of trading opportunities, etc., is huge.  

A big problem in this task was to find the correct versions of each of the modules, something which took roughly 4-5 hours of trial and error, before even attempting to work/code with these protocols. 

After creating the correct files, developing a celery config file, creating tasks, hitting the correct API endpoints, setting up the database message broker, and attempting to run the worker, there was still an error regarding the worker reaching an end of file, meaning no tasks were being noticed. 
This was a result of imports in the settings file which are default to Django, so I changed this file accordingly, only to be met with another error, still regarding the worker. 
After about an hour of research I found that it was a problem exclusive to windows (Redis is not typically supported officially on Windows),  and was solved by downloading eventlet, which allowed me to ensure the concurrent nature of the workers. 

Finally, a JavaScript file handles the messages which are received. 

As it stands, the application “beats” every 5 seconds to fetch a new price, however this may be changed at a later date to a less frequent beat, as more often than not the beat simply returns the same price as the previous iteration. 10 seconds will likely be a good number, however this will be covered in my next wave of continuous testing which will take place shortly, after which the appropriate number will be determined more finely.  

The next task is to compress the process of running each server/worker/beat/etc. into a single procfile script. Until then however, I thought it would be both amusing and helpful to document the current process necessary to receive live data through sockets:

![images](docs/blog/images/messyTerminals.JPG)


## Update on LSTM and Amazon AWS Integration - 23/02/1018
### LSTM
The LSTM has been fixed to generate appropriate predictions even with the addition of litecoin, which was a problem in the previous blog post. In order to achieve this, I had to fix an issue with the historical data set for litecoin and bitcoin, and re train the models. Despite this, I believe I am still overfitting and though I am happy for now, the LSTM network is still not as refined as I would like it to be.

### AWS
An AWS EC2 (Elastic Compute Cloud) Ubuntu server with Tensorflow has been established and the Machine learning module has been transferred there to train, run, generate images and save them at fixed intervals. My plan is to run the single step prediction daily after each candle close, and the 5 day prediction every Monday.
In order to achieve this, I utilised Putty, and WinSCP to transfer the code. The server chosen simply utilises 8gb of ram and 4 virtual cores, which should be plenty considering the data I am working with is not very stressful, and considering that the single step prediction can be carried out relatively quickly. Unfortunately I do feel the need to train the model daily as I believe the cryptocurrency market in particular is so volatile that the user can benefit from the most up to date information available. However I will decide this in light of further testing.
The application will pull data from the AWS server at fixed intervals, or perhaps simply constantly be watching a URL that the server posts the images to. Regardless, This architectural design means that in the event of a loss of server uptime, I now have the capacity to revert to a local version of the LSTM prediction module, meaning the user is guaranteed less downtime.


## AWS - EC2, S3 and DynamoDB Initial Integration Completed - 01/03/2018
In order to set up the Machine Learning code on AWS, I have had to make some changes to the planned architecture of the project. This, as mentioned previously, will allow for a more lightweight application, and reduce/eliminate any potential slow-down or concurrency issues with running a learning model in the Django application. Currently, I have an EC2 (Elastic Cloud) instance running in Ohio, U.S.A, which is housing my machine learning code. The server I have chosen is Amazon's tensorflow enabled, machine learning-geared "c5.xlarge" server type.


I am making use of putty and WinSCP in order to transfer files from my local machine to the EC2 server, and to gain access to the server's terminal.
![images](docs/blog/images/puttywinscp.JPG)



I have also adjusted the python code such that after certain variables are calculated (such as the predictions, as well as the MatPlotLib images), they are automatically sent to an S3 bucket which I have also set up, also located in Ohio. This allows me to simply reference images statically in my Django application, meaning no JSON needs to be utilized in order to get an up to date image of prediction accuracy, training and test set model data, mean average error (MAE) graphs, etc. as the s3 bucket creates a URL for each of its objects.


Finally, I have also set up a DynamoDB database on AWS, which stores various information that is to be displayed in the front end of the application. At the moment, this includes the coin ID, the date, the prediction, the 5 day model prediction, and the previous day’s closing price (will be used in a later sprint to calculate the prediction accuracy once more data is available).
![images](docs/blog/images/dbInAWS.JPG)



In order to do this, I created AWS config and credential files, and configured the private and public keys both on the AWS EC2 instance side, and also on my own local server which the Django app is hosted on. The reason both servers needed the authentication is to write to the DB from the EC2 cloud server, and read from it on the Django side.

![images](docs/blog/images/accesskeysetup.JPG)



The following is an example of writing to the DB, and is code which is located on the AWS server.

![images](docs/blog/images/codeForTableInsert.JPG)




In order to read from the DB on my own server (app-side) I am utilizing boto3, which is a library for communicating with AWS via a command-line interface (CLI). After parsing the JSON result of the call from my application, the following is the type of result I receive back. 

![images](docs/blog/images/itemGetSucceed.JPG)




This makes it easy to simply parse the specific information I need from the JSON dump. At the moment, each time the homepage is loaded, data is fetched from the AWS database and displayed in the table beneath the "coin of the day" chart. This chart simply displays a graph that has been identified as the most likely to have a successful day according to the previous night's single-step prediction.


As mentioned previously, this new architecture allows me to very quickly query a DB on the application side in order to update fields which would have otherwise required overuse of sockets. While sockets will still be utilized on the front end, the reliability of a fixed DB is vastly superior for the type of data which will be displayed on the home page, considering it is not a page from which the user will be making trades, and therefore does not require second by second updates.

Overall I am happy with my progress architecturally, and am now beginning to implement the real-time chart analysis, for which I intendd to make use of the AWS database to store and visualize data on. This will involve also establishing a means of alerting the user on the occurrence of significant events which may be of interest to them.


## Project Progress pt 1: Forex Predictions/Automatic Strategy - success! 18/03/2018

I have finally found a strategy and ml method that works well with the currently supported forex options, which uses gradient boosting classification. Using this method, I scan through the historical data for each currency and assign “green” or profitable days a score of 0 and “red” days a score of 1. Based on this information, and the normalized price data for each currency, the model is trained. Then on the most recent 5% of data, the model is tested and attempted to predict whether the next day will be assigned a 0 or 1.  This method is preferable in comparison to an LSTM Network approach as is used in cryptocurrencies, because the variance in price is so small that it is fruitless to attempt to predict the actual closing price. In fact, this made me question whether or not such a prediction is even necessary for cryptocurrencies considering the only purpose of the project as outlined in the functional specification was to predict price direction. I am  considering implementing this method in cryptocurrencies also, to examine the correlation between the LSTM’s prediction vs that of the Gradient boosting classifier. 

 

This method is most successful on the Euro and the British Pound, presumably because the variance is not as large and traditionally the corresponding economies are not as volatile in comparison to the CNY. Nevertheless, all three currencies are profitable trades under this model. 
 

To test this assertion, I took an imaginary 10,000 USD initial capital and made trades based off the 0 or 1 value for each prediction. In doing so, all coins achieved a profit factor of above 1.

 
![images](docs/blog/images/forexStats.JPG)

 

It is important to note that this data is based off daily values, simply as a proof of concept. This algorithm makes use of nothing but normalized closing price for candlesticks and as such could be applied to any time frame, meaning there is a nice opportunity for higher frequency trading options – perhaps even automated – assuming a similar profit factor can be achieved on the 1m or 5m time frame. 

 

As well as this, I am considering adding an option to establish an automatic trading strategy which has its foundation in this prediction.

## Project Progress pt 2: Chart Analysis - Trend/Support/Resistance levels/Alerts - success (almost)! 18/03/2018


Project Progress pt 2: Chart Analysis - Trend/Support/Resistance levels/Alerts - success (almost)!
March 18, 2018

As it stands, I have implemented my own chart analysis software, without the use of any APIs and libraries. As such, there are still some bugs to be ironed out but if I was to put a number on it I would estimate I am north of 70% complete. 

 

The code collects the previous 30 days of data from coinmarketcap, and then parses it into a Pandas data frame with columns Date, Open, High, Low and Close. 


From this data, I treat each row as a “candlestick”. If a day’s candlestick is a higher close than the previous days, then it is treated as green, if lower, it is treated as red. 

 

With this data, I start from t-30 days and analyze each “candle” one at a time. After each candle, the code assigns a color to that candle, as well as a current trend – either “bear”, “bull”, or “tightening”. 

 

Based off the candles color and current trend, this reduces the list of possibilities for the next candle. This pattern continues until the current day-1 where we can conclude the current state of the market according to the charts, and suggest possible actions based on this fact. 

 

Below is already an out-of-date screengrab but it gives an idea of how the UI will work.

 

![images](docs/blog/images/breakdown.JPG)

 

 

Clearly the code could pick out an established support at 175 dollars, and also recognize when that support was broken. At this point, the user would have been alerted, had they been subscribed to that coin (in this case, Litecoin (LTC)). 

 

I am very excited with this aspect of the system and am looking forward to polishing it off. 

 

In terms of visualizing the chart as seen above, I have actually created my own candlesticks using the open high low close data mentioned previously. To do this, I had to convert the data frame to a json object and clean up the data so that it was in the correct format to feed into chartJS. ChartJS does not have a library for candlestick charts natively, so I am making use of amCharts to display the candles I built.


## Progress Update - 02/04/2018

### Trading:

The trading UI has been upgraded to be more usable. This includes a larger trade window, options for indicators and Drawing tools, tradeview live chat, and details from the platforms chart analysis and machine learning predictions tools to give the user an idea of the state of the market, in the same view that trading is possible. Still to do here is the addition of support and resistance levels from chart analysis tool, which will be pulled from the AWS hosted NoSQL DB.


### Data Analytics:

There is now support for both intraday and historical tracking of a user trades, the various markets which they trade, their positions, and how their positions change over time, as well as how the size of their trades vary over time. 
Architecturally, throughout the day, user trade data will be added to a NoSQL table, and at midnight each night, the table will be wiped clean and all the data inside it will be processed into a single row of another NoSQL table, which represents the historical data.   


### To do:

Still to do is to add additional features to the LSTM models such as the result of running the same Gradient Boosting Classifier on them (as is done with forex), and actually adding that as a column to train on. EMA (exponential moving average) is also to be added. 
As well as this I plan to update the chart analysis tool to better find support and resistance levels.

## AWS, User Alerts, Chart Analysis Rework, LSTM New Models, User auth, Android App - 15/04/2018
### AWS
Crontab has been set up on the AWS EC2 instance in order to schedule the tasks to run daily as planned. 
This includes the prediction for cryptocurrency prices, which will take place each night at 11.am, for the next day. 
As well as this, at 11.55, the Forex prediction which is quicker as it uses a gradient boosting classifier, is ran. 
Finally, I run the python script which cleans up the day's intraday trading database, formulates a single row with all the data, inserts it into the daily database, and wipes clean the intraday DB. This python script is running at 11.59, thanks to DynamoDB which has extremely fast read/write capabilities.

### User Alerts
As well as the above, I wish to create a new crontab for User alerts. This will run every minute and ensure that prices which users have set for alerts are not hit. If they are, the user will be alerted accordingly. Originally I was planning to make use of Java script to complete this task, however dealing with the prices on the back end gives me far more flexibility in terms of the type of alert I want to issue. This includes things like email/text message/Android application etc. 

### Chart analysis Rework
The chart analysis tool has been improved to also find next-level support and resistance lines if they exist. This means that a user can now watch for the break of tighter trends, and if they do break, have an idea of what the next target will be in terms of taking profit (hopefully!). This has been achieved by splitting the data sets into their respective 4 points of a candle as before, but this time each point is compared against all other arrays of points to find points which are of less than a 5% deviance from each other. These points are all stored in a separate array, and then compared against the current price to determine whether or not they are support or resistance lines. 

The current price is then compared against this array to check for the closest pair of lines above and below the current price, and subsequently the next pair is also found for our support 2 and resistance 2 targets.

### LSTM new Models:
In order to achieve a more specific result, especially for litecoin, considering its data is different than bitcoin and ethereum’s considering it has not been on the market for as long, and essentially only has a few months(!) of data at current prices.

To compensate, I created a new model for litecoin and added some extra features to train on, as well as increasing the number of neurons or layers in the network to give more importance to these new features.

These features included my own time series calculations of real-time relative strength index, 100 day moving averages, and normalized price. 

As well as this I have updated the analytics page on my application to give a more aesthetically pleasing representation of LSTM accuracy, as well as other data such as trading stats and profit made using the LSTM's recommendation over the past X number of days. 

### User Auth
In anticipation of the Android application and subsequent auth keys that will be needed to receive notifications, I have created user authentication on the application which will be used both to link user's to their exchange accounts to be able to trade from within the application, and also to link to their android app, so that notifications can be received when subscribed markets break support or resistance levels. 

### Android App
The android application has also been developed in a very basic form. At the moment, I am still working on receiving notifications in firebase, though the back-end of the actual triggering is working already, as I have achieved SMS notification using Twilio.


## Fixed Flaw in profit calculation method - 04/05/2018
In the cryptocurrency predictive method a flaw was found which would give inaccurate results, as the parameter being passed was a data frame rather than dataframe.values, which correctly up-casts the type within the data frame.
The result of this fix was that models which are already profitable (BTC, ETH), have been shown to be more profitable than previously stated, however the Litecoin model which was already performing worse, has had its poor performance amplified.


## User Interface Change
The user interface has been changed to reflect a more mature and somber colour theme of greys and off white. It is undecided as of yet if this theme will be permanent. A survey is currently being carried out which will determine how a random sample of users from Dublin City University respond to each of the color themes, as well as other aspects of the project's interface.

## Documentation
The Technical Guide has been completed for the project aside from the final diagram which will be a class diagram. The headings included are motivation, research, design, implementation, problems solved, and results.
The user manual is currently being written. 

## Testing
Testing has also been completed and uploaded to Git, however an amendment will be made when the results of the aforementioned survey have returned. In terms of testing types, each aspect of this project (AWS helpers, Django application, Android application), has been tested to 80% coverage minimum using automated unit tests. 
The User interface for the android application has been tested using Espresso, and the Django user interface using TestCase library native to Django.

### Refactoring 
PyLint has been used to test the style and error/bug potential of code on the AWS server and in the Django application, and refactoring has been carried out to ensure all code scores above average. This included indentation amendments, removing redundant imports, adding docstrings to each function and class (https://docs.python.org/3/tutorial/controlflow.html#documentation-strings), as well as shortening methods, etc. 

### Back testing ML Models
Back testing the machine learning models has been fixed as mentioned in the previous blog, in the case of LSTM models for cryptocurrencies. While the methods have not changed, an incorrect parameter was previously being passed to the evaluation method, which was under-representing the performance of the models.
Below are the results of the most recent back test of the models:

![images](docs/blog/images/latest-tests.JPG)

The FX models are being back tested with $10,000 capital initial investment to determine the profit the user would have made had they followed the trades suggested day by day.

### User testing
User testing has been carried out both by 3rd parties and by myself. 3rd parties tested the various functionality of the product form a usage and design perspective, and testing carried out on the developer side of things included boundary value testing, stress testing, and authentication testing. 

### Results
The results of the testing phase of development can be reviewed in greater detail in the testing document which will be appended to the end of my technical guide.



