library(data.table)

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
d <- d[,.(red, green, blue, alt = (alt - mean(alt)) / sd(alt), lat = (lat - mean(lat)) / sd(lat), lon = (lon - mean(lon)) / sd(lon))]

krige.matrix <- make.krige.matrix( d[,.(lat, lon)])



min.lon <- min(d$lon)
max.lon <- max(d$lon)
min.lat <- min(d$lat)
max.lat <- max(d$lat)

r <- 0.06
dlon = r * 2 * sin(pi / 3);
dlat = r * 1.5;
lat <- min.lat
odd <- F

hex <- array(0, dim = c(0, 2))

repeat {
  if (lat >= max.lat + r) break

  if (odd) {
    lon <- min.lon + dlon / 2
  } else {
    lon <- min.lon
  }

  repeat {
    if (lon >= max.lon + dlon / 2) break

    hex <- rbind(hex, c(lat, lon))

    lon <- lon + dlon
  }
  odd <- !odd
  lat <- lat + dlat
}

h <- data.frame(lat = hex[,1], lon = hex[,2])
p.alt <- krige.predict.vector(h, d[,.(lat, lon)], krige.matrix, d$alt)
#p.red <- krige.predict.vector(h, d[,.(lat, lon)], krige.matrix, d$red)
#p.blue <- krige.predict.vector(h, d[,.(lat, lon)], krige.matrix, d$blue)
#p.green <- krige.predict.vector(h, d[,.(lat, lon)], krige.matrix, d$green)
p.col <- find.nearest.colours(h, d)
h$alt <- p.alt
h$red <- p.col$red
h$green <- p.col$green
h$blue <- p.col$blue

h2 <- data.frame(lat = hex[,1], lon = hex[,2])
h2$alt <- clusterise(h$alt, 8)
h2$red <- h$red
h2$green <- h$green
h2$blue <- h$blue

#h$red <- p.red
#h$green <- p.green
#h$blue <- p.blue

info <- data.frame(radius = r, dlat= dlat, dlon = dlon)

write.table(info, "../data/hex.csv", row.names = F, append = F, sep=",")
write.table(h, "../data/hex.csv", row.names = F, append = T, sep=",")

write.table(info, "../data/hex2.csv", row.names = F, append = F, sep=",")
write.table(h2, "../data/hex2.csv", row.names = F, append = T, sep=",")
