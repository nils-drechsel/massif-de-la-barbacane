library(data.table)
library(png)

f.linear <- function(a) {
  a
}

dst <- function(a, b) {
  sqrt((a[1] - b[1])^2 + (a[2] - b[2])^2)
}

make.krige.matrix <- function(d) {
  k <- as.matrix(dist(d))
  k <- cbind(k, 1)

  k <- rbind(k, 1)
  k[nrow(k), ncol(k)] <- 0
  k
}

make.krige.vector <- function(d, x) {
  v <- as.matrix(apply(as.matrix(d), 1, dst, b=x))
  v <- rbind(v, 1)
  v
}

krige.predict <- function(x, d, krige.matrix, values) {
  v <- make.krige.vector(d[,.(lat, lon)], x)
  w <- solve(krige.matrix,v)
  w <- w[-c(length(w))]
  w %*% matrix(values, length(values), 1)
}

krige.predict.vector <- function(vec, d, krige.matrix, values) {
  apply(vec, 1, krige.predict, d=d, krige.matrix=krige.matrix, values = values)
}

nearest.colour <- function(x, d) {
  distances <- unlist(apply(as.matrix(d[,.(lat, lon)]), 1, dst, as.vector(x)))
  i <- which(distances == min(distances))[1]
  c(d$red[i], d$green[i], d$blue[i])
}

find.nearest.colours <- function(h, d) {
  cols <- array(0, dim=c(0, 3))
  for (i in 1:nrow(h)) {
    cols <- rbind(cols, nearest.colour(h[i,], d))
  }
  df <- as.data.frame(cols)
  names(df) <- c("red", "green", "blue")
  df
}

clusterise <- function(x, n) {
  minx <- min(x)[1]
  maxx <- max(x)[1]
  cl <- c()
  r <- seq(minx, maxx, length.out = n)
  for (y in x) {
    for (i in 1:n) {
      if (y <= r[i] || i >= n) {
        cl <- c(cl, r[i])
        break
      }
    }
  }
  cl
}


m <- read.csv("../data/data.csv")
m <- data.table(m)
d <- m[,.(red = mean(red), blue = mean(blue), green = mean(green)), by = .(alt, lat, lon)]
print(paste("lon/lat:", (max(d$lon) - min(d$lon)) / (max(d$lat) - min(d$lat)), sep = " "))
d <- d[,.(red, green, blue, alt = (alt - mean(alt)) / sd(alt), lat = (lat - mean(lat)) / sd(lat), lon = (lon - mean(lon)) / sd(lon))]

krige.matrix <- make.krige.matrix( d[,.(lat, lon)])



min.lon <- min(d$lon)
max.lon <- max(d$lon)
min.lat <- min(d$lat)
max.lat <- max(d$lat)

resolution = 300

df.lon.seq = data.frame(lon = seq(from = min.lon, to = max.lon, length.out=resolution))
df.lat.seq = data.frame(lat = seq(from = min.lat, to = max.lat, length.out=resolution))

df <- merge.data.frame(df.lon.seq, df.lat.seq)

altitude <- krige.predict.vector(df, d[,.(lat, lon)], krige.matrix, d$alt)

altitude.constrained <- (altitude - min(altitude)) / (max(altitude) - min(altitude))


n.planes = 20

planes <- seq(from=0, to=1, length.out = n.planes)

cap <- function(x, planes) {
  p <- x - planes
  p <- p[p>=0]
  planes[length(p)]
}


altitude.bitmap <- matrix(0, resolution, resolution)

for (y in 1:resolution) {
  for (x in 1:resolution) {
    altitude.bitmap[x,y] <- cap(altitude.constrained[(y-1)*resolution + (x-1) + 1], planes)
  }
}

for (y in 1:resolution) {
  for (x in 1:resolution) {
    altitude.bitmap[y,x] <- altitude.constrained[(y-1)*resolution + (x-1) + 1]
  }
}

p.red <- krige.predict.vector(df, d[,.(lat, lon)], krige.matrix, d$red)
p.blue <- krige.predict.vector(df, d[,.(lat, lon)], krige.matrix, d$blue)
p.green <- krige.predict.vector(df, d[,.(lat, lon)], krige.matrix, d$green)

colour.bitmap <- array(0, dim=c(resolution, resolution, 3))

for (y in 1:resolution) {
  for (x in 1:resolution) {
    colour.bitmap[y,x,1] <- p.red[(y-1)*resolution + (x-1) + 1]
    colour.bitmap[y,x,2] <- p.green[(y-1)*resolution + (x-1) + 1]
    colour.bitmap[y,x,3] <- p.blue[(y-1)*resolution + (x-1) + 1]
  }
}



writePNG(altitude.bitmap, "../data/heightfield.png")
writePNG(colour.bitmap, "../data/heightfield_texture.png")
