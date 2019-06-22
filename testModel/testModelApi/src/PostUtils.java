
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
//        String pathname = "input.txt"; // ����·�������·�������ԣ�д���ļ�ʱ��ʾ���·��,��ȡ����·����input.txt�ļ�
        //��ֹ�ļ��������ȡʧ�ܣ���catch��׽���󲢴�ӡ��Ҳ����throw;
        //���ر��ļ��ᵼ����Դ��й¶����д�ļ���ͬ��
        //Java7��try-with-resources�������Źر��ļ����쳣ʱ�Զ��ر��ļ�����ϸ���https://stackoverflow.com/a/12665271
        try {
        	FileInputStream fis = new FileInputStream(pathname);   
        	InputStreamReader isr = new InputStreamReader(fis, "UTF-8"); 
            BufferedReader br = new BufferedReader(isr); // ����һ�����������ļ�����ת�ɼ�����ܶ���������
         
            String line;
            //�����Ƽ����Ӽ���д��
            while ((line = br.readLine()) != null) {
                // һ�ζ���һ������
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
		String pathname1 = root + "2.������������.txt";
		String pathname2 = root + "2.����.txt";
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
        //HTTPЭ��
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
			/*���SINPUT output������cache*/
            conn.setDoInput(true);
            conn.setDoOutput(true);
            conn.setUseCaches(false);
			/*���÷��͵ķ�ʽ*/
            conn.setRequestMethod("POST");
			/*�O��ͷ*/
            conn.setRequestProperty("Connection", "Keep-Alive");
            conn.setRequestProperty("Charset", "UTF-8");
            conn.setRequestProperty("Content-Type", "multipart/form-data;boundary="+boundary);

			/*�O��DataOutputStream*/
            DataOutputStream ds = new DataOutputStream(conn.getOutputStream());

            ds.writeBytes(twoHyphens+boundary+end);
            ds.writeBytes("Content-Disposition: form-data;"+"name=\"token\""+end);
            ds.writeBytes(end);
            ds.writeBytes(token);
            ds.writeBytes(end);

            ds.writeBytes(twoHyphens+boundary+end);
            ds.writeBytes("Content-Disposition: form-data;"+"name=\"file\";filename=\""+fileName+"\""+end);
            ds.writeBytes(end);



			/*ȡ���ļ���FileInputStream*/
            FileInputStream fStream = new FileInputStream(uploadFile);
            int bufferSize = 1024;
            byte[] buffer = new byte[bufferSize];
            int length = -1;
			/*���ļ���ȡ�����ݻ�����*/
            while((length = fStream.read(buffer))!=-1){
                ds.write(buffer,0,length);
            }
            ds.writeBytes(end);
            ds.writeBytes(twoHyphens+boundary+twoHyphens+end);
            fStream.close();
            ds.flush();

            if (conn.getResponseCode() == 200) {
                // ��ȡ��Ӧ������������
                InputStream is = conn.getInputStream();
                // �����ֽ����������
                ByteArrayOutputStream message = new ByteArrayOutputStream();
                // �����ȡ�ĳ���
                int len = 0;
                // ���建����
                byte buffer2[] = new byte[1024];
                // ���ջ������Ĵ�С��ѭ����ȡ
                while ((len = is.read(buffer2)) != -1) {
                    // ���ݶ�ȡ�ĳ���д�뵽os������
                    message.write(buffer2, 0, len);
                }
                // �ͷ���Դ
                is.close();
                message.close();
                // �����ַ���
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
            //��������ʽ,����ʱ��Ϣ
            conn.setRequestMethod("POST");
            conn.setReadTimeout(5000);
            conn.setConnectTimeout(5000);
            //������������,���:
            conn.setDoOutput(true);
            conn.setDoInput(true);
            //Post��ʽ���ܻ���,���ֶ�����Ϊfalse
            conn.setUseCaches(false);
            //�������������:
          /*  String data = "token="+ URLEncoder.encode("3bc05d37782e4c14202fdbf69af72df2", "UTF-8")+
                    "&time="+ URLEncoder.encode("2017-07-10 18:42:56", "UTF-8")+
                    "&clickId="+ URLEncoder.encode("5", "UTF-8")+
                    "&commentedId="+ URLEncoder.encode("5", "UTF-8")+
                    "&typeId="+ URLEncoder.encode("2", "UTF-8")+
                    "&commentText="+ URLEncoder.encode("��������", "UTF-8")+
                    "&clickTableId=" + URLEncoder.encode("7", "UTF-8");*/
            //�������дһЩ����ͷ�Ķ���...
            //��ȡ�����
            OutputStream out = conn.getOutputStream();
            out.write(data.getBytes());
            out.flush();
            if (conn.getResponseCode() == 200) {
                // ��ȡ��Ӧ������������
                InputStream is = conn.getInputStream();
                // �����ֽ����������
                ByteArrayOutputStream message = new ByteArrayOutputStream();
                // �����ȡ�ĳ���
                int len = 0;
                // ���建����
                byte buffer[] = new byte[1024];
                // ���ջ������Ĵ�С��ѭ����ȡ
                while ((len = is.read(buffer)) != -1) {
                    // ���ݶ�ȡ�ĳ���д�뵽os������
                    message.write(buffer, 0, len);
                }
                // �ͷ���Դ
                is.close();
                message.close();
                // �����ַ���
                msg = new String(message.toByteArray());
                return msg;
            }
        }catch(Exception e){e.printStackTrace();}
        return msg;
    }
}