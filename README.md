# Semantic Segmentation

### Overview
Fully Convolutional Network (FCN) based on the VGG-16 image classifier for performing semantic segmentation to identify drivable road area from images taken from a front-facing camera on a car. Images are taken from the [Kitti Road dataset](http://www.cvlibs.net/datasets/kitti/eval_road.php) donwloadable [here](http://www.cvlibs.net/download.php?file=data_road.zip).  

### Architecture
There are several unique aspects to a Fully Convolutional Network that are implemented in this model:
* Encoder - VGG-16 model pre-trained on ImageNet extracts features from the image. Instead of a fully connected output layer, as is typical in a fully connected CNN, the fully connected layer is replaced by a 1x1 convolutional layer. The output tensor will remain 4-D instead of flattening to 2-D, thus retaining spatial information
* Decoder - Use transposed convolutions to upsample the output of the 1x1 convolutional layer to the size of the original image. A transposed convolution is essentially a reverse forward convolution. 
* Add skip connections using the output of the 3rd, 4th, and 7th VGG layers. The skip connections allow the decoder to use information from multiple resolutions and allow for a more precise segmentation decisions. 

#### Hyperparameters
* Loss Function = cross-entropy
* Optimizer = AdamOptimizer
* keep_prob = 0.75
* learning_rate = 0.0001
* epochs = 25
* batch_size = 2

### Results
Cross-Entropy Loss = 0.00029

[sample](./output/1.png)
[sample](./output/2.png)
[sample](./output/3.png)
[sample](./output/4.png)
[sample](./output/5.png)
[sample](./output/6.png)
[sample](./output/7.png)
[sample](./output/8.png)
[sample](./output/9.png)
[sample](./output/10.png)
