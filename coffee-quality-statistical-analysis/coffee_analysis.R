# load and attach ---------------------------------------------------------

coffee = na.omit(read.csv("coffee_quality.csv"))
attach(coffee)



# tests on expected value -------------------------------------------------

# from my experience, coffees from Africa are far superior
# test whether expected value of their quality is higher than in Asia or Americas
tcp.africa = TotalCupPoints[Continent == "Africa"]          # mean = 84.626
tcp.asia = TotalCupPoints[Continent == "Asia"]              # mean = 84.024   
tcp.south = TotalCupPoints[Continent == "South America"]    # mean = 83.068
tcp.north = TotalCupPoints[Continent == "North America"]    # mean = 83.277

t.test(tcp.asia, tcp.africa, alternative = "less")    # p-value = 0.0229
t.test(tcp.south, tcp.africa, alternative = "less")   # p-value = 0.0008237
t.test(tcp.north, tcp.africa, alternative = "less")   # p-value = 3.093e-05

# it is a "known fact" that the higher the coffee grows, the more time it takes
# to ripen, therefore seeds can absorb more flavor from the pulp
# test whether we expect higher quality with higher altitude

threshold = 1500  
tcp.high = TotalCupPoints[Altitude > threshold]        # mean = 84.340
tcp.low  = TotalCupPoints[Altitude <= threshold]       # mean = 83.436
t.test(tcp.lower, tcp.higher, alternative = "less")    # p-value = 6.001e-06

# I was not able to pinpoint my preference between natural and washed processing
# method
# test whether expected qualities are equal for both processing methods
tcp.natural = TotalCupPoints[ProcessingMethod == "Natural / Dry"] # mean = 83.679
tcp.washed = TotalCupPoints[ProcessingMethod == "Washed / Wet"]   # mean = 83.633
t.test(tcp.natural, tcp.washed, alternative = "two.sided")   # p-value = 0.8917



# tests on probability ----------------------------------------------------

# in recent years, Gesha variety of Arabica coffee has grown in popularity
# due to its unique characteristics and rarity

# get 95% confidence interval of the ratio of Gesha variety trees being 
# cultivated to all Arabica trees (I wasn't able to find an estimate
# to use for the test)
n.geshas = sum(Variety == "Gesha")
n = length(Variety)
p.geshas = n.geshas / n     # p = 0.133

L = p.geshas - sqrt(p.geshas*(1 - p.geshas)/n)*qt(0.975, df=n-1)
U = p.geshas + sqrt(p.geshas*(1 - p.geshas)/n)*qt(0.975, df=n-1)
c(L, U)     # (L, U) = (0.0865, 0.1809)

# Panamian Gesha is a popular variety, but it originated from Ethiopia
# test, whether the percentage of Gesha trees is the same in North
# America and Africa
n.geshas.north = sum(Variety[Continent == "North America"] == "Gesha")
n.north = sum(Continent == "North America")
p.north = n.geshas.north / n.north   # p.north = 0.0937

n.geshas.africa = sum(Variety[Continent == "Africa"] == "Gesha")
n.africa = sum(Continent == "Africa")
p.africa = n.geshas.africa / n.africa      # p.africa = 0.0435

T.geshas = (p.north-p.africa) / sqrt(
  p.north*(1 - p.north)/n.north
  + p.africa*(1 - p.africa)/n.africa
  )

2*( 1-pt(abs(T.geshas), df = n.north + n.africa - 2))  # p-value = 0.3718522



# regression model --------------------------------------------------------

# TotalCupPoints is a metric directly calculated from scores in categories
# like Aroma, Flavor, Body, Acidity, Balance... However, these are not easily
# distinguishable for an amateur coffee enjoyer. Therefore, I would like to try
# to model TotalCupPoints by something more easilty noticable and that is
# Altitude, Aroma, Acidity and whether the coffee is from Gesha variety
Gesha = as.numeric(Variety=="Gesha")
model = lm(TotalCupPoints ~ Altitude + Aroma + Acidity + Gesha, x=TRUE)

model$coefficients
# (Intercept)     Altitude        Aroma      Acidity        Gesha 
#3.371731e+01 1.376287e-05 2.761900e+00 3.721877e+00 1.462523e-01 

# to compare the significance of coefficients, we need to Z-scale the data
model.scaled = lm(
  TotalCupPoints ~ scale(Altitude) + scale(Aroma) + scale(Acidity) + Gesha, 
  x=TRUE
  )
model.scaled$coefficients
# (Intercept) scale(Altitude)    scale(Aroma)  scale(Acidity)           Gesha 
#83.684708849     0.006786842     0.801963627     0.972223327     0.146252312 

# for further analysis, visualize and test normality of the residuals
X = model$x
beta.hat = model$coefficients
residuals = (X %*% beta.hat) - TotalCupPoints

shapiro.test(residuals)     # p-value = 0.1162
hist(residuals, breaks = "FD")

# also, we can plot prediction compared to true values, whether they 
# are located uniformly "around" y=x line
plot((model$x %*% model$coefficients), TotalCupPoints, xlab="Predictions",
     main="Predictions vs TotalCupPoints")
abline(c(0,1))



# contrast testing --------------------------------------------------------

# I want to test the relevance of the beta parameters
contrast.test = function(a, beta, X, y){  # adapted from 9.r
	n = length(y)
	k = length(beta)
	
	SSE = sum((y - X%*%beta)^2)
	S = sqrt(SSE / (n-k))

	standard.error = S * sqrt(t(a) %*% solve(t(X)%*%X) %*% a)
	
	T = t(a) %*% beta / standard.error
	return(2 * (1 - pt(abs(T), df=n-k)))
}

# test whether influence of altitude is not equal to zero
contrast.test(a=c(0,1,0,0,0), beta=beta.hat, X=X, y=TotalCupPoints)   # p-value = 0.8566182

# test whether influence of coffee being Gesha variety is not equal to zero
contrast.test(a=c(0,0,0,0,1), beta=beta.hat, X=X, y=TotalCupPoints)   # p-value = 0.2172516

# test whether influence of aroma and acidity is not the same
contrast.test(a=c(0,0,1,-1,0), beta=beta.hat, X=X, y=TotalCupPoints)  # p-value = 0.008286998



# submodel testing --------------------------------------------------------
submodel.test = function(beta, X, y){   # adapted from 9.r
  n = length(y)
	k = length(beta)
	
	SSE = sum((y - X%*%beta)^2)
	
	submodel = lm(y ~ 1, x=TRUE)
	SSE.submodel = sum((y - submodel$x %*% submodel$coefficients)^2)
	
	F = ((SSE.submodel - SSE) / (k - 1)) / (SSE / (n - k))
	return(1 - pf(F, df1=k-1, df2=n-k))
}

# test whether a simple intercept prediction is performs similarly or better
# to our model
submodel.test(beta=beta.hat, X=X, y=TotalCupPoints)    # p-value = 0



# test parallelity of models ----------------------------------------------

# we want to test, whether constructing different models for different
# processing methods is relevant and yields significantly different parameters

# construct model for washed process
Washed = ProcessingMethod == "Washed / Wet"
model.washed = lm(
  TotalCupPoints[Washed] ~ (
    Altitude[Washed] + Aroma[Washed] + Acidity[Washed] + Gesha[Washed]
    ), 
  x=TRUE
  )
beta.washed = model.washed$coeff
X.washed = model.washed$x

# construct model for natural process
Natural = ProcessingMethod == "Natural / Dry"
model.natural = lm(
  TotalCupPoints[Natural] ~ (
    Altitude[Natural] + Aroma[Natural] + Acidity[Natural] + Gesha[Natural]
    ), 
  x=TRUE
  )
beta.natural = model.natural$coeff
X.natural = model.natural$x

# join the data matrices and beta vectors to simulate one model
X.joined = rbind(
  cbind(X.washed, matrix(0, nrow = nrow(X.washed), ncol=ncol(X.natural))),
   cbind(matrix(0, nrow = nrow(X.natural), ncol=ncol(X.washed)), X.natural)
)
beta.joined = c(beta.washed, beta.natural)

# contrast test whether the predicted hyperplanes are not parallel
a.parallel = c(0, rep(1, ncol(X.washed) - 1), 0, rep(-1, ncol(X.natural) - 1))
test.contrast(
  a = a.parallel, beta=beta.joined,
  X=X.joined, y=c(TotalCupPoints[Washed], TotalCupPoints[Natural])
  )    # p-value = 0.7814283

# contrast test whether the predicted hyperplanes are not identical
a.identical = c(rep(1, ncol(X.washed)), rep(-1, ncol(X.natural)))
test.contrast(
  a = a.identical, beta=beta.joined,
  X=X.joined, y=c(TotalCupPoints[Washed], TotalCupPoints[Natural])
  )   # p-value = 0.5889759

