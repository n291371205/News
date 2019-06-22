
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLEncoder;
import java.util.concurrent.CountDownLatch;

import net.sf.json.JSONObject;



public class PostUtils {
    public static String [] readFile(String pathname) {
    	String [] strArr = new String[20];
    	int i = 0;
//        String pathname = "input.txt"; // 绝对路径或相对路径都可以，写入文件时演示相对路径,读取以上路径的input.txt文件
        //防止文件建立或读取失败，用catch捕捉错误并打印，也可以throw;
        //不关闭文件会导致资源的泄露，读写文件都同理
        //Java7的try-with-resources可以优雅关闭文件，异常时自动关闭文件；详细解读https://stackoverflow.com/a/12665271
        try {
        	FileInputStream fis = new FileInputStream(pathname);   
        	InputStreamReader isr = new InputStreamReader(fis, "UTF-8"); 
            BufferedReader br = new BufferedReader(isr); // 建立一个对象，它把文件内容转成计算机能读懂的语言
         
            String line;
            //网友推荐更加简洁的写法
            while ((line = br.readLine()) != null) {
                // 一次读入一行数据
            	strArr[i] = line;
            	i++;
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        String [] retArr = new String[i];
        for (int j = 0; j < retArr.length; j++) {
			retArr[j] = strArr[j];
		}
        return retArr;
    }
    
    public static void main(String[] args) {
		String url = "http://localhost:5000/get_sim";
		JSONObject json = new JSONObject();
		String root = "C:/Users/kid/Desktop/model/data/news/";
		String pathname1 = root + "2.美国军费扩张.txt";
		String pathname2 = root + "2.雾霾.txt";
		json.put("1", readFile(pathname1));
		json.put("2", readFile(pathname2));
//		
//		System.out.println(json.toString());
		
//		String data = "";
		String data = null;
		try {
			data = "json=" + URLEncoder.encode(json.toString(), "UTF-8");
		} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		String returnStr = PostUtils.sendPost(url, data);
		System.out.println(returnStr);
    }

    public static boolean saveUrlAs(String photoUrl,String fileName){
        //HTTP协议
        try {
            URL url = new URL(photoUrl);
            HttpURLConnection connection =(HttpURLConnection)url.openConnection();
            DataInputStream in = new DataInputStream(connection.getInputStream());
            DataOutputStream out = new DataOutputStream(new FileOutputStream(fileName));
            byte []buffer = new byte[4096];
            int count = 0;
            while((count=in.read(buffer))>0){
                out.write(buffer,0,count);
            }
            out.close();
            in.close();
            return true;
        } catch (MalformedURLException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
            return false;
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
            return false;
        }
    }

    public static String uploadFile(String url,String fileName,String uploadFile,String token){
        String end = "\r\n";
        String twoHyphens = "--";
        String boundary = "*****";
        String msg = "";

        try {
            HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
			/*允許INPUT output不允许cache*/
            conn.setDoInput(true);
            conn.setDoOutput(true);
            conn.setUseCaches(false);
			/*设置发送的方式*/
            conn.setRequestMethod("POST");
			/*設置头*/
            conn.setRequestProperty("Connection", "Keep-Alive");
            conn.setRequestProperty("Charset", "UTF-8");
            conn.setRequestProperty("Content-Type", "multipart/form-data;boundary="+boundary);

			/*設置DataOutputStream*/
            DataOutputStream ds = new DataOutputStream(conn.getOutputStream());

            ds.writeBytes(twoHyphens+boundary+end);
            ds.writeBytes("Content-Disposition: form-data;"+"name=\"token\""+end);
            ds.writeBytes(end);
            ds.writeBytes(token);
            ds.writeBytes(end);

            ds.writeBytes(twoHyphens+boundary+end);
            ds.writeBytes("Content-Disposition: form-data;"+"name=\"file\";filename=\""+fileName+"\""+end);
            ds.writeBytes(end);



			/*取得文件的FileInputStream*/
            FileInputStream fStream = new FileInputStream(uploadFile);
            int bufferSize = 1024;
            byte[] buffer = new byte[bufferSize];
            int length = -1;
			/*从文件读取到数据缓冲区*/
            while((length = fStream.read(buffer))!=-1){
                ds.write(buffer,0,length);
            }
            ds.writeBytes(end);
            ds.writeBytes(twoHyphens+boundary+twoHyphens+end);
            fStream.close();
            ds.flush();

            if (conn.getResponseCode() == 200) {
                // 获取响应的输入流对象
                InputStream is = conn.getInputStream();
                // 创建字节输出流对象
                ByteArrayOutputStream message = new ByteArrayOutputStream();
                // 定义读取的长度
                int len = 0;
                // 定义缓冲区
                byte buffer2[] = new byte[1024];
                // 按照缓冲区的大小，循环读取
                while ((len = is.read(buffer2)) != -1) {
                    // 根据读取的长度写入到os对象中
                    message.write(buffer2, 0, len);
                }
                // 释放资源
                is.close();
                message.close();
                // 返回字符串
                msg = new String(message.toByteArray());
                return msg;
            }


        } catch (MalformedURLException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return msg;
    }


    public static String sendPost(String url,String data)
    {
        String msg = "";
        try{
            HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
            //设置请求方式,请求超时信息
            conn.setRequestMethod("POST");
            conn.setReadTimeout(5000);
            conn.setConnectTimeout(5000);
            //设置运行输入,输出:
            conn.setDoOutput(true);
            conn.setDoInput(true);
            //Post方式不能缓存,需手动设置为false
            conn.setUseCaches(false);
            //我们请求的数据:
          /*  String data = "token="+ URLEncoder.encode("3bc05d37782e4c14202fdbf69af72df2", "UTF-8")+
                    "&time="+ URLEncoder.encode("2017-07-10 18:42:56", "UTF-8")+
                    "&clickId="+ URLEncoder.encode("5", "UTF-8")+
                    "&commentedId="+ URLEncoder.encode("5", "UTF-8")+
                    "&typeId="+ URLEncoder.encode("2", "UTF-8")+
                    "&commentText="+ URLEncoder.encode("零零落落", "UTF-8")+
                    "&clickTableId=" + URLEncoder.encode("7", "UTF-8");*/
            //这里可以写一些请求头的东东...
            //获取输出流
            OutputStream out = conn.getOutputStream();
            out.write(data.getBytes());
            out.flush();
            if (conn.getResponseCode() == 200) {
                // 获取响应的输入流对象
                InputStream is = conn.getInputStream();
                // 创建字节输出流对象
                ByteArrayOutputStream message = new ByteArrayOutputStream();
                // 定义读取的长度
                int len = 0;
                // 定义缓冲区
                byte buffer[] = new byte[1024];
                // 按照缓冲区的大小，循环读取
                while ((len = is.read(buffer)) != -1) {
                    // 根据读取的长度写入到os对象中
                    message.write(buffer, 0, len);
                }
                // 释放资源
                is.close();
                message.close();
                // 返回字符串
                msg = new String(message.toByteArray());
                return msg;
            }
        }catch(Exception e){e.printStackTrace();}
        return msg;
    }
}