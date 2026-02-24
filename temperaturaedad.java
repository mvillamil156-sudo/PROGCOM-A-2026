/******************************************************************************
temp=float("Temperatura registrada:")
if temp>=27: print("Póngase ag¿lgo fresco")
elif temp>20 and temp<=27: print("Abríguese")
elif temp>=16 and temp<20: print("Abríguese más")
else: print("Está helando")

*******************************************************************************/
import java.util.*;
public class Main
{
	public static void main(String[] args) {
	    
		System.out.println("Temperatura registrada:");
		Scanner leer=new Scanner(System.in);
		//nextLine es para String
		//nextFloat es para Flotantes
		float temp=leer.nextFloat();
		//&& and || or
		if (temp>=27){System.out.println("Póngase algo más fresco");}
		else if(temp>=20 && temp<27){System.out.println("Abríguese");}
		else if(temp>=16 && temp<20){System.out.println("Abríguese más");}
		else {System.out.println("Está helado");}
		
		int edad =leer.nextInt();
		System.out.println(edad>=18? "Eres mayor de edad": "No eres mayor de edad");

	}
}