# This script only parameterizes the original script to make python compatible (makeboxplot_rev3.R)
python_arglist <- commandArgs(trailingOnly = TRUE)
arglist_length = as.numeric(length(python_arglist))

inputfilename <- python_arglist[1]
outputfilename <- python_arglist[2]

rvector_genes <- python_arglist[-c(1,2)]
rvector_genes
vgenes_length = length(rvector_genes)

# ----------------------------------------------------------------------------------------------------
# Below is R-script

datf <- read.csv(inputfilename, stringsAsFactors = FALSE, header=TRUE)
datfb <- t(datf)

#remove exxtraneous 
datf_2 <- as.data.frame(datfb)
colnames(datf_2) <- as.character(unlist(datf_2[2,]))

datf_4 <- datf_2[-c(1:2),]

# prep for melt
datf_4$"Group" <- paste(datf_4[,2],datf_4[,1], sep="_")
num_row = nrow(datf_4)
datf_4$"ID" <- 1:num_row

vgenes <- rvector_genes
vgenes2 <- c("Group", "ID", vgenes)

idx_colnames <- which(colnames(datf_4) %in% vgenes2)
idx_colnames

select_matrix <- datf_4[, c(idx_colnames)]
select_matrix2 <- select_matrix
select_matrix3 <- select_matrix

#Method1_ log
v_length <- as.numeric(length(idx_colnames)) -2 #this is a bug length of somesort, needs to be changed manually
for(int_x in c(1:v_length)){
  select_matrix2[,int_x] <- log2(as.numeric(as.character(select_matrix2[,int_x])))
  #now[getting rid of -inf]
  char_temp <- as.character(select_matrix2[,int_x])
  char_temp[char_temp=="-Inf"] <- "-20.0"
  select_matrix2[,int_x] <- as.numeric(char_temp)
}

#Method2_ log
mylog <- function(df){
  return(log2(as.numeric(as.character(df))))
}
select_matrix3[,c(1:v_length)] <- apply(select_matrix3[,c(1:v_length)], 2, mylog)

#trying to scale matric
select_matrix2[,c(1:v_length)] <- scale(select_matrix2[,c(1:v_length)],center=TRUE,scale=FALSE)

#class(dat_3$`1-Methyladenosine`)
# load library
library(ggplot2)
library(tidyr)
library(ggthemes)
library(reshape2)

# Melt - consoidates data from multple cols to few, readable into ggplot format
df3 <- melt(select_matrix2,id.vars=c("ID","Group"))

windows()
ggplot(data=df3) + 
  geom_boxplot( aes(x=variable, y=value,  fill=Group))+ #, position=position_dodge(0.85)) + 
  scale_x_discrete(name="Gene") +
  scale_fill_manual(values=c("#C1E7B5", "#E8ACBC", "#387723", "#FC0505")) +
  scale_y_continuous(name="Log Fold-change", breaks=seq(-10,10,2), limits=c(-10,10)) + 
  #coord_cartesian(ylim = c(-14.0,14.0)) +
  theme_minimal() + 
  #geom_text(data =aggregate(value~var,df, mean), aes(x=var, y = 2.5, label=round(labels[,3],3)), angle=90) +
  theme(axis.text.x = element_text(angle=0, size=14))
#geom_text(aes(x=factor(var), y=value, label="label", hjust = -0.3))

#print(myplot)
#dev.off()
ggsave(outputfilename)

#tinker around with some graphs, scale, normalization, then data