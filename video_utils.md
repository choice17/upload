/*

video utils

1. pgm
2. 

*/

#include "video_codec.h"
#include "image.h"
#include "error.h"
#include "util.h"
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libswscale/swscale.h>
#include <libavutil/imgutils.h>
#include <libavutil/opt.h>

#include <stdio.h>
#include <stdlib.h>

typedef struct {
	uint8_t *data;
	int width;
	int height;
	int channel;
} Image;

void save_gray_image(unsigned char *buf, int wrap, int x_size, int y_size, int frame)
{
	char frame_filename[1024];
	snprintf(frame_filename, sizeof(frame_filename), "frame_%d.pgm", frame);
	FILE *f;
	int i;
	f = fopen(frame_filename, "wb");

	fprintf(f, "P5\n%d %d\n%d\n", x_size, y_size, 255);

	int byte = x_size * y_size;
	fwrite(buf, sizeof(char), byte, f);

	fclose(f);
}

//#define FFMPEG_TRANSFORM

void debug()
{
	av_log_set_level(AV_LOG_INFO);
}

static int fill_stream_info(AVStream *av_stream, AVCodec **av_codec, AVCodecContext **av_codecCtx)
{
	//find decoder from stream
	*av_codec = avcodec_find_decoder(av_stream->codecpar->codec_id);
	if (!*av_codec) {
		logging("failed to find the codec");
		return FAILURE;
	}
	//alloc context for codec
	*av_codecCtx = avcodec_alloc_context3(*av_codec);
	if (!*av_codecCtx) {
		logging("failed to alloc memory for codec context");
		return FAILURE;
	}
	//copy codec par
	if (avcodec_parameters_to_context(*av_codecCtx, av_stream->codecpar) < 0) {
		logging("failed to fill codec context");
		return FAILURE;
	}
	//init context
	if (avcodec_open2(*av_codecCtx, *av_codec, NULL) < 0) {
		logging("failed to open codec");
		return FAILURE;
	}

	return SUCCESS;
}

int open_media(const char *filename, AVFormatContext **avFmtCtx)
{
	//alloc AVFormatContext
	*avFmtCtx = avformat_alloc_context();
	if (!*avFmtCtx) {
		logging("failed to alloc memory for format");
		return FAILURE;
	}
	//lloading AVFormatContext
	if (avformat_open_input(avFmtCtx, filename, NULL, NULL) != 0) {
		logging("failed to open input file %s", filename);
		return FAILURE;
	}

	//Read packets of a media file to get stream information
	//This is useful for file formats with no headers such as MPEG
	if (avformat_find_stream_info(*avFmtCtx, NULL) < 0) {
		logging("failed to get stream info");
		return FAILURE;
	}

	return SUCCESS;
}

int prepare_decoder(StreamingContext *decoder)
{
	for (int i = 0; i < decoder->avFmtCtx->nb_streams; i++) {
		if (decoder->avFmtCtx->streams[i]->codecpar->codec_type == AVMEDIA_TYPE_VIDEO) {
			decoder->video_stream = decoder->avFmtCtx->streams[i];
			decoder->video_index = i;

			if (fill_stream_info(decoder->video_stream, &decoder->video_codec, &decoder->video_codecCtx) !=
			    SUCCESS) {
				return FAILURE;
			}
		} else {
			logging("skipping streams other than audio and video");
		}
	}

	return SUCCESS;
}

int prepare_encoder(StreamingContext *encoder, AVCodecContext *decoder_ctx, AVRational input_framerate,
                    StreamingParams sp)
{
	encoder->video_stream = avformat_new_stream(encoder->avFmtCtx, NULL);

	encoder->video_codec = avcodec_find_encoder_by_name(sp.video_codec);
	if (!encoder->video_codec) {
		logging("could not find the proper codec");
		return FAILURE;
	}

	encoder->video_codecCtx = avcodec_alloc_context3(encoder->video_codec);
	if (!encoder->video_codecCtx) {
		logging("could not allocated memory for codec context");
		return FAILURE;
	}

	av_opt_set(encoder->video_codecCtx->priv_data, "preset", "fast", 0);
	if (sp.codec_priv_key && sp.codec_priv_value) {
		av_opt_set(encoder->video_codecCtx->priv_data, sp.codec_priv_key, sp.codec_priv_value, 0);
	}
	encoder->video_codecCtx->height = decoder_ctx->height;
	encoder->video_codecCtx->width = decoder_ctx->width;
	encoder->video_codecCtx->sample_aspect_ratio = decoder_ctx->sample_aspect_ratio;

	if (encoder->video_codec->pix_fmts) {
		encoder->video_codecCtx->pix_fmt = encoder->video_codec->pix_fmts[0];
	} else {
		encoder->video_codecCtx->pix_fmt = decoder_ctx->pix_fmt;
	}

	encoder->video_codecCtx->bit_rate = 2 * 1000 * 1000;
	encoder->video_codecCtx->rc_buffer_size = 4 * 1000 * 1000;
	encoder->video_codecCtx->rc_max_rate = 2 * 1000 * 1000;
	encoder->video_codecCtx->rc_min_rate = 2.5 * 1000 * 1000;

	encoder->video_codecCtx->time_base = av_inv_q(input_framerate);
	encoder->video_stream->time_base = encoder->video_codecCtx->time_base;

	if (avcodec_open2(encoder->video_codecCtx, encoder->video_codec, NULL) < 0) {
		logging("could not open the codec");
		return FAILURE;
	}
	avcodec_parameters_from_context(encoder->video_stream->codecpar, encoder->video_codecCtx);
	return SUCCESS;
}

int copy_encoder(StreamingContext *encoder, AVCodecParameters *decoder_para)
{
	encoder->video_stream = avformat_new_stream(encoder->avFmtCtx, NULL);

	avcodec_parameters_copy(encoder->video_stream->codecpar, decoder_para);

	encoder->video_codec = avcodec_find_encoder(encoder->video_stream->codecpar->codec_id);
	if (!encoder->video_codec) {
		logging("could not find the proper codec");
		return FAILURE;
	}

	encoder->video_codecCtx = avcodec_alloc_context3(encoder->video_codec);
	if (!encoder->video_codecCtx) {
		logging("could not allocated memory for codec context");
		return FAILURE;
	}

	if (avcodec_parameters_to_context(encoder->video_codecCtx, encoder->video_stream->codecpar) < 0) {
		logging("failed to copy codec params to codec context");
		return FAILURE;
	}
	return SUCCESS;
}

int encode_frame(StreamingContext *decoder, StreamingContext *encoder, AVFrame *input_frame)
{
	if (input_frame) {
		input_frame->pict_type = AV_PICTURE_TYPE_NONE;
	}

	AVPacket *output_packet = av_packet_alloc();
	if (!output_packet) {
		logging("could not allocate memory for output packet");
		return FAILURE;
	}

	int response = avcodec_send_frame(encoder->video_codecCtx, input_frame);

	while (response >= 0) {
		response = avcodec_receive_packet(encoder->video_codecCtx, output_packet);
		if (response == AVERROR(EAGAIN) || response == AVERROR_EOF) {
			break;
		} else if (response < 0) {
			logging("Error while receiving packet from encoder: %s", av_err2str(response));
			return FAILURE;
		}
		output_packet->stream_index = decoder->video_index;
		output_packet->duration = encoder->video_stream->time_base.den / encoder->video_stream->time_base.num /
		                          decoder->video_stream->avg_frame_rate.num *
		                          decoder->video_stream->avg_frame_rate.den;

		av_packet_rescale_ts(output_packet, decoder->video_stream->time_base, encoder->video_stream->time_base);

		response = av_interleaved_write_frame(encoder->avFmtCtx, output_packet);
		if (response != 0) {
			logging("Error %d while receiving packet from decoder: %s", response, av_err2str(response));
			return FAILURE;
		}
	}
	av_packet_unref(output_packet);
	av_packet_free(&output_packet);
	return SUCCESS;
}

int decode_packet(AVCodecContext *pCodecContext, AVPacket *input_packet, AVFrame *output_frame, int frame_no)
{
	int response = avcodec_send_packet(pCodecContext, input_packet);

	if (response < 0) {
		return FAILURE;
	}

	while (response >= 0) {
		response = avcodec_receive_frame(pCodecContext, output_frame);
		if (response == AVERROR(EAGAIN) || response == AVERROR_EOF) {
			break;
		} else if (response < 0) {
			return FAILURE;
		}

		if (response >= 0) {
			if (frame_no == pCodecContext->frame_number - 1) {
				return FINISH;
			}
		}
	}
	return SUCCESS;
}

int transform_pixel_format(AVFrame *in_frame, AVFrame *out_frame, AVCodecContext *pCodecContext,
                           enum AVPixelFormat in_pixFmt, enum AVPixelFormat out_pixFmt)
{
	struct SwsContext *sws_ctx;

	sws_ctx = sws_getContext(pCodecContext->width, pCodecContext->height, in_pixFmt, pCodecContext->width,
	                         pCodecContext->height, out_pixFmt, SWS_BILINEAR, NULL, NULL, NULL);

	sws_scale(sws_ctx, (uint8_t const *const *)in_frame->data, in_frame->linesize, 0, pCodecContext->height,
	          out_frame->data, out_frame->linesize);

	return SUCCESS;
}

#ifdef FFMPEG_TRANSFORM
int avframe_to_image(AVFrame *pFrame, Image *image)
{
	int size_per_channel = image->width * image->height;
	for (int h = 0; h < image->height; h++) {
		memcpy(image->data + image->width * h, pFrame->data[0] + pFrame->linesize[0] * h, image->width);
		memcpy(image->data + 1 * size_per_channel + image->width * h, pFrame->data[1] + pFrame->linesize[1] * h,
		       image->width);
		memcpy(image->data + 2 * size_per_channel + image->width * h, pFrame->data[2] + pFrame->linesize[2] * h,
		       image->width);
	}
	return SUCCESS;
}

#else
int avframe_to_image(AVFrame *pFrame, Image *image)
{
	int size_per_channel = image->width * image->height;
	int u_value, v_value;

	memcpy(image->data, pFrame->data[0], size_per_channel);

	for (int y = 0; y < image->height; y += 2) {
		for (int x = 0; x < image->width; x += 2) {
			u_value = *(pFrame->data[1] + pFrame->linesize[1] * y / 2 + x / 2);
			image->data[size_per_channel + y * image->width + x] = u_value;
			image->data[size_per_channel + y * image->width + x + 1] = u_value;
			image->data[size_per_channel + (y + 1) * image->width + x] = u_value;
			image->data[size_per_channel + (y + 1) * image->width + x + 1] = u_value;

			v_value = *(pFrame->data[2] + pFrame->linesize[2] * y / 2 + x / 2);
			image->data[2 * size_per_channel + y * image->width + x] = v_value;
			image->data[2 * size_per_channel + y * image->width + x + 1] = v_value;
			image->data[2 * size_per_channel + (y + 1) * image->width + x] = v_value;
			image->data[2 * size_per_channel + (y + 1) * image->width + x + 1] = v_value;
		}
	}
	return SUCCESS;
}
#endif

int image_to_avframe(Image *image, AVFrame *pFrame)
{
	int size_per_channel = image->width * image->height;
	for (int h = 0; h < image->height; h++) {
		memcpy(pFrame->data[0] + pFrame->linesize[0] * h, image->data + image->width * h, image->width);
		memcpy(pFrame->data[1] + pFrame->linesize[1] * h, image->data + 1 * size_per_channel + image->width * h,
		       image->width);
		memcpy(pFrame->data[2] + pFrame->linesize[2] * h, image->data + 2 * size_per_channel + image->width * h,
		       image->width);
	}
	return SUCCESS;
}

int alloc_frame_dataBuf(AVFrame *pFrame, AVCodecContext *pCodecContext, enum AVPixelFormat pixFmt, uint8_t **buffer)
{
	int numBytes;

	numBytes = av_image_get_buffer_size(pixFmt, pCodecContext->width, pCodecContext->height, 1);

	*buffer = (uint8_t *)av_malloc(numBytes * sizeof(uint8_t));

	return SUCCESS;
}

int read_image(ObjectInfo *object_info, int obj, int frame_no, Image *image)
{
	int response = 0;

	StreamingContext *decoder = (StreamingContext *)calloc(1, sizeof(StreamingContext));
	decoder->filename = object_info[obj].video_name;

	if (open_media(decoder->filename, &decoder->avFmtCtx) != SUCCESS) {
		return FAILURE;
	}

	if (prepare_decoder(decoder) != SUCCESS) {
		return FAILURE;
	}

	AVFrame *input_frame = av_frame_alloc();
	if (!input_frame) {
		logging("failed to allocated memory for AVFrame");
		return -1;
	}

	AVFrame *output_frame = av_frame_alloc();
	if (!output_frame) {
		logging("failed to allocated memory for AVFrame");
		return -1;
	}

	uint8_t *output_buffer = NULL;
	if (alloc_frame_dataBuf(output_frame, decoder->video_codecCtx, AV_PIX_FMT_YUV444P, &output_buffer)) {
		logging("failed to allocated data memory for AVFrame");
		return -1;
	}

	av_image_fill_arrays(output_frame->data, output_frame->linesize, output_buffer, AV_PIX_FMT_YUV444P,
	                     decoder->video_codecCtx->width, decoder->video_codecCtx->height, 1);

	AVPacket *input_packet = av_packet_alloc();
	if (!input_packet) {
		logging("failed to allocated memory for AVPacket");
		return -1;
	}

	// int fps = decoder->video_stream->r_frame_rate.num;
	// AVRational timeBase = decoder->video_stream->time_base;
	// int frame_pos = (timeBase.den / fps) * frame_no;

	// int ret = av_seek_frame(decoder->avFmtCtx, decoder->video_index, frame_pos, AVSEEK_FLAG_ANY);

	int start = 0;
	int nb_gop = -1;
	int i = 0;
	int target_gop = frame_no / 20;
	frame_no = frame_no % 20;
	while (av_read_frame(decoder->avFmtCtx, input_packet) >= 0) {
		if (decoder->avFmtCtx->streams[input_packet->stream_index]->codecpar->codec_type ==
		    AVMEDIA_TYPE_VIDEO) {
			char *data = input_packet->data;
			data += 4;
			if (*data == 0x67) {
				nb_gop++;
			}
			if (nb_gop == target_gop && *data == 0x67) {
				start = 1;
			}

			if (start == 1) {
				response = decode_packet(decoder->video_codecCtx, input_packet, input_frame, frame_no);

				if (response == FAILURE) {
					logging("failure to decode packet");
					break;
				}

				else if (response == FINISH) {
					if (transform_pixel_format(input_frame, output_frame, decoder->video_codecCtx,
					                           AV_PIX_FMT_YUV420P, AV_PIX_FMT_YUV444P) != SUCCESS) {
						return FAILURE;
					}
#ifdef FFMPEG_TRANSFORM
					if (avframe_to_image(output_frame, image) != SUCCESS) {
						return FAILURE;
					}
#else
					if (avframe_to_image(input_frame, image) != SUCCESS) {
						return FAILURE;
					}
#endif
					break;
				}
			}
		}
		av_packet_unref(input_packet);
	}

	av_packet_free(&input_packet);
	av_frame_free(&input_frame);
	av_frame_free(&output_frame);

	avformat_close_input(&decoder->avFmtCtx);
	avformat_free_context(decoder->avFmtCtx);
	decoder->avFmtCtx = NULL;

	avcodec_free_context(&decoder->video_codecCtx);
	decoder->video_codecCtx = NULL;

	free(decoder);
	decoder = NULL;

	return SUCCESS;
}



/*

1. read h264
2. parse sei
3. read frame
3.1 open video
3.2 open decoder
3.3 open sws scale
3.4 transform image format
4. image processsing
5. write frame
5.1 open video
5.2 open encoder
5.3 setup encoder parameter
5.4 write

*/

#include "app.h"
#include "error.h"
#include "algo.h"
#include "video_codec.h"
#include "image.h"
#include "util.h"
#include <libavutil/imgutils.h>
#include <libavutil/opt.h>

static void encode(AVCodecContext *enc_ctx, AVFrame *frame, AVPacket *pkt, FILE *outfile)
{
	int ret;

	/* send the frame to the encoder */
	if (frame)
		printf("Send frame %3" PRId64 "\n", frame->pts);

	ret = avcodec_send_frame(enc_ctx, frame);
	if (ret < 0) {
		fprintf(stderr, "Error sending a frame for encoding\n");
		exit(1);
	}

	while (ret >= 0) {
		ret = avcodec_receive_packet(enc_ctx, pkt);
		logging("error msg %s", av_err2str(ret));
		if (ret == AVERROR(EAGAIN)) {
			logging("it is EAGAIN");
		}
		if (ret == AVERROR(EAGAIN) || ret == AVERROR_EOF)
			break;
		else if (ret < 0) {
			fprintf(stderr, "Error during encoding\n");
			exit(1);
		}

		printf("Write packet %3" PRId64 " (size=%5d)\n", pkt->pts, pkt->size);
		fwrite(pkt->data, 1, pkt->size, outfile);
	}
	av_packet_unref(pkt);
}

int main(int argc, char **argv)
{
	debug();

	const char *video_list_name = "file_list.txt"; //argv[1];
	const char *object_info_name = "data.csv"; //argv[2];
	const char *out_file_name = "out.mp4"; //argv[3];

	VideoInfo *video_info = NULL;
	ObjectInfo *object_info = NULL;

	int final_length = 0;
	int max_frame_need = 0;
	bool *object_validity = NULL;
	int *frame_shift = NULL;

	// parse object info

	if (create_videoInfo(&video_info) != SUCCESS) {
		//error handling
		return FAILURE;
	}
	if (create_objectIno(&object_info) != SUCCESS) {
		//error handling
		return FAILURE;
	}

	ObjectMode mode = PARSE_FROM_FILE;
	if (parse_obj_info(video_list_name, object_info_name, mode, video_info, object_info) != SUCCESS) {
		//error handling
		return FAILURE;
	}

	//object schedule
	...	

	const char *codec_name = "libx264";

	StreamingContext *encoder = (StreamingContext *)calloc(1, sizeof(StreamingContext));
	encoder->filename = out_file_name;

	//分配記憶體給輸出的AVFormatContext
	avformat_alloc_output_context2(&encoder->avFmtCtx, NULL, NULL, encoder->filename);
	if (!encoder->avFmtCtx) {
		logging("could not allocate memory for output format");
		return FAILURE;
	}

	encoder->video_codec = avcodec_find_encoder(AV_CODEC_ID_H264);
	if (!encoder->video_codec) {
		logging("Codec '%s' not found", codec_name);
		return FAILURE;
	}

	encoder->video_codecCtx = avcodec_alloc_context3(encoder->video_codec);
	if (!encoder->video_codecCtx) {
		logging("Could not allocate video codec context");
		return FAILURE;
	}

	int ret = 0;

	/* put sample parameters */
	encoder->video_codecCtx->bit_rate = 2000000;
	encoder->video_codecCtx->width = 1920;
	encoder->video_codecCtx->height = 1080;
	encoder->video_codecCtx->framerate = (AVRational){ 25, 1 };
	encoder->video_codecCtx->time_base = (AVRational){ 1, 25 };

	encoder->video_codecCtx->gop_size = 10;
	encoder->video_codecCtx->max_b_frames = 0;
	encoder->video_codecCtx->pix_fmt = AV_PIX_FMT_YUV420P;

	if (encoder->video_codec->id == AV_CODEC_ID_H264) {
		av_opt_set(encoder->video_codecCtx->priv_data, "preset", "slow", 0);
	}

	ret = avcodec_open2(encoder->video_codecCtx, encoder->video_codec, NULL);
	if (ret < 0) {
		logging("Could not open codec: %s", av_err2str(ret));
	}

	AVFrame *input_frame = av_frame_alloc();
	if (!input_frame) {
		logging("failed to allocated memory for AVFrame");
		return -1;
	}
	input_frame->format = AV_PIX_FMT_YUV444P;
	input_frame->width = encoder->video_codecCtx->width;
	input_frame->height = encoder->video_codecCtx->height;
	ret = av_frame_get_buffer(input_frame, 0);
	//ret = av_image_alloc(input_frame->data, input_frame->linesize, input_frame->width, input_frame->height, (enum AVPixelFormat)input_frame->format, 1);
	// if (ret < 0) {
	//     logging("Could not allocate the video frame data");
	//     return FAILURE;
	// }
	/*
	uint8_t *input_buffer = NULL;
	if (alloc_frame_dataBuf(input_frame, encoder->video_codecCtx, AV_PIX_FMT_YUV444P, &input_buffer)) {
		logging("failed to allocated data memory for AVFrame"); 
		return -1;
	}
	*/

	AVFrame *output_frame = av_frame_alloc();
	if (!output_frame) {
		logging("failed to allocated memory for AVFrame");
		return -1;
	}
	output_frame->format = AV_PIX_FMT_YUV420P;
	output_frame->width = encoder->video_codecCtx->width;
	output_frame->height = encoder->video_codecCtx->height;
	ret = av_frame_get_buffer(output_frame, 0);

	FILE *fp_out = fopen(out_file_name, "wb");

	AVPacket *output_packet = av_packet_alloc();
	if (!output_packet) {
		logging("could not allocate memory for output packet");
		return FAILURE;
	}

    for(int f=0;f<final_length;f++){
	    fflush(stdout);

	    Image *img_out = NULL;
	    if (create_image(video_info->width, video_info->height, 1, &img_out) != SUCCESS) {
		    //error handling
		    return FAILURE;
	    }

	    if (combine_frame(f, object_info, frame_shift, object_validity, max_frame_need, img_out) != SUCCESS) {
		    //error handling
		    return FAILURE;
	    }
	    logging("combine_frame %d", f);

	    /*
		av_image_fill_arrays(input_frame->data, input_frame->linesize, input_buffer,
					AV_PIX_FMT_YUV444P, encoder->video_codecCtx->width,
					encoder->video_codecCtx->height, 1);
		
		av_image_fill_arrays(output_frame->data, output_frame->linesize, output_buffer,
					AV_PIX_FMT_YUV420P, encoder->video_codecCtx->width,
					encoder->video_codecCtx->height, 1);
		*/
	    if (image_to_avframe(img_out, input_frame) != SUCCESS) {
		    return FAILURE;
	    }

	    transform_pixel_format(input_frame, output_frame, encoder->video_codecCtx, AV_PIX_FMT_YUV444P,
		                   AV_PIX_FMT_YUV420P);

	    //encode_frame(decoder, encoder, output_frame);
	    // if (input_frame){
	    // 	input_frame->pict_type = AV_PICTURE_TYPE_NONE;
	    // }

	    /* make sure the frame data is writable */
	    ret = av_frame_make_writable(output_frame);
	    if (ret < 0) {
		    logging("Output frame is not writeable : %d", ret);
		    return FAILURE;
	    }

	    output_frame->pts = f;

	    encode(encoder->video_codecCtx, output_frame, output_packet, fp_out);


	    if (destroy_image(1, img_out) != SUCCESS) {
		    //error handling
		    return FAILURE;
	    }
    }

    uint8_t endcode[] = { 0, 0, 1, 0xb7 };
    encode(encoder->video_codecCtx, NULL, output_packet, fp_out);
    if (encoder->video_codec->id == AV_CODEC_ID_MPEG1VIDEO || encoder->video_codec->id == AV_CODEC_ID_MPEG2VIDEO)
	    fwrite(endcode, 1, sizeof(endcode), fp_out);
    fclose(fp_out);
    //av_write_trailer(encoder->avFmtCtx);

    av_frame_free(&input_frame);
    av_frame_free(&output_frame);

    av_packet_free(&output_packet);

    avformat_free_context(encoder->avFmtCtx);
    encoder->avFmtCtx = NULL;

    avcodec_free_context(&encoder->video_codecCtx);
    encoder->video_codecCtx = NULL;

    free(encoder);
    encoder = NULL;

	return 0;
}
